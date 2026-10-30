import streamlit as st
import json
from datetime import datetime, date
from src.database.connection import DatabaseConnection
from src.database.models import (
    Applicant, LoanApplication, CreditHistory, RiskIndicators,
    ApplicationEvaluation, AuditLog, EmploymentStatus, LoanType, ApplicationStatus, Classification
)
from src.orchestrator import LoanApplicationOrchestrator
from src.utils import get_logger

logger = get_logger(__name__)

# Initialize database connection
DatabaseConnection.init_db()

# Initialize orchestrator
orchestrator = LoanApplicationOrchestrator()

# Streamlit configuration
st.set_page_config(
    page_title="Loan Application Analysis System",
    page_icon="💰",
    layout="wide"
)

st.title("🏦 Multi-Agent Loan Application Analysis System")
st.markdown("Automated loan application evaluation using specialized AI agents")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Submit Application", "View Applications", "Application Details", "Analytics"]
)

def render_dashboard():
    """Render main dashboard"""
    st.header("Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    db = DatabaseConnection.get_session()

    with col1:
        total_apps = db.query(LoanApplication).count()
        st.metric("Total Applications", total_apps)

    with col2:
        approved = db.query(LoanApplication).filter(
            LoanApplication.status == ApplicationStatus.APPROVED
        ).count()
        st.metric("Approved", approved)

    with col3:
        rejected = db.query(LoanApplication).filter(
            LoanApplication.status == ApplicationStatus.REJECTED
        ).count()
        st.metric("Rejected", rejected)

    with col4:
        pending = db.query(LoanApplication).filter(
            LoanApplication.status == ApplicationStatus.MANUAL_REVIEW
        ).count()
        st.metric("Manual Review", pending)

    # Recent applications
    st.subheader("Recent Applications")
    recent_apps = db.query(LoanApplication).order_by(LoanApplication.application_date.desc()).limit(10).all()

    if recent_apps:
        for app in recent_apps:
            applicant = db.query(Applicant).filter(Applicant.id == app.applicant_id).first()
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.write(f"**{applicant.first_name} {applicant.last_name}**")

            with col2:
                st.write(f"${float(app.loan_amount):,.2f}")

            with col3:
                st.write(f"{app.loan_type.value}")

            with col4:
                status_color = "🟢" if app.status == ApplicationStatus.APPROVED else "🔴" if app.status == ApplicationStatus.REJECTED else "🟡"
                st.write(f"{status_color} {app.status.value}")

            with col5:
                if st.button("View", key=f"recent_{app.id}"):
                    st.session_state.selected_app_id = app.id
                    st.rerun()
    else:
        st.info("No applications yet")

    db.close()

def render_submit_application():
    """Render application submission form"""
    st.header("Submit New Loan Application")

    with st.form("loan_application_form"):
        st.subheader("Applicant Information")

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
        with col2:
            last_name = st.text_input("Last Name")

        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email")
        with col2:
            phone = st.text_input("Phone")

        col1, col2 = st.columns(2)
        with col1:
            ssn = st.text_input("SSN (masked as ***-**-****)")
        with col2:
            dob = st.date_input("Date of Birth")

        col1, col2 = st.columns(2)
        with col1:
            address = st.text_input("Address")
        with col2:
            city = st.text_input("City")

        col1, col2, col3 = st.columns(3)
        with col1:
            state = st.text_input("State", max_chars=2)
        with col2:
            zip_code = st.text_input("Zip Code", max_chars=10)
        with col3:
            employment_status = st.selectbox(
                "Employment Status",
                [e.value for e in EmploymentStatus]
            )

        col1, col2 = st.columns(2)
        with col1:
            annual_income = st.number_input("Annual Income", min_value=0.0, step=1000.0)
        with col2:
            years_employed = st.number_input("Years Employed", min_value=0, step=1)

        st.subheader("Loan Details")

        col1, col2 = st.columns(2)
        with col1:
            loan_amount = st.number_input("Loan Amount", min_value=0.0, step=1000.0)
        with col2:
            loan_type = st.selectbox("Loan Type", [l.value for l in LoanType])

        col1, col2 = st.columns(2)
        with col1:
            loan_purpose = st.text_input("Loan Purpose")
        with col2:
            loan_term = st.number_input("Loan Term (months)", min_value=1, step=1)

        submitted = st.form_submit_button("Submit Application", type="primary")

        if submitted:
            if not all([first_name, last_name, email, annual_income, loan_amount]):
                st.error("Please fill in all required fields")
                return

            try:
                db = DatabaseConnection.get_session()

                # Create applicant
                applicant = Applicant(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    ssn=ssn,
                    date_of_birth=dob,
                    address=address,
                    city=city,
                    state=state,
                    zip_code=zip_code,
                    employment_status=EmploymentStatus(employment_status),
                    annual_income=annual_income,
                    years_employed=years_employed
                )
                db.add(applicant)
                db.flush()

                # Create loan application
                loan_app = LoanApplication(
                    applicant_id=applicant.id,
                    loan_amount=loan_amount,
                    loan_purpose=loan_purpose,
                    loan_type=LoanType(loan_type),
                    loan_term_months=loan_term,
                    status=ApplicationStatus.UNDER_REVIEW
                )
                db.add(loan_app)
                db.commit()

                application_id = loan_app.id

                st.success(f"Application submitted successfully! Application ID: {application_id}")
                st.info("Starting automated evaluation...")

                # Run evaluation
                result = orchestrator.evaluate_application(application_id)

                if result.get("status") == "completed":
                    st.success("✅ Evaluation complete!")
                    st.json(result.get("final_decision"))
                else:
                    st.error(f"Evaluation failed: {result.get('error')}")

                db.close()

            except Exception as e:
                st.error(f"Error submitting application: {str(e)}")
                logger.error(f"Application submission error: {str(e)}")

def render_view_applications():
    """Render applications list"""
    st.header("View All Applications")

    db = DatabaseConnection.get_session()

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All"] + [s.value for s in ApplicationStatus]
        )

    col1, col2 = st.columns(2)
    with col1:
        min_amount = st.number_input("Min Loan Amount", min_value=0.0, step=1000.0)
    with col2:
        max_amount = st.number_input("Max Loan Amount", min_value=0.0, value=1000000.0, step=1000.0)

    # Query
    query = db.query(LoanApplication)

    if status_filter != "All":
        query = query.filter(LoanApplication.status == ApplicationStatus(status_filter))

    query = query.filter(
        LoanApplication.loan_amount >= min_amount,
        LoanApplication.loan_amount <= max_amount
    )

    applications = query.order_by(LoanApplication.application_date.desc()).all()

    if applications:
        for app in applications:
            applicant = db.query(Applicant).filter(Applicant.id == app.applicant_id).first()
            evaluation = db.query(ApplicationEvaluation).filter(
                ApplicationEvaluation.application_id == app.id
            ).first()

            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 1, 1])

                with col1:
                    st.write(f"**{applicant.first_name} {applicant.last_name}**")
                    st.caption(f"App ID: {app.id}")

                with col2:
                    st.write(f"${float(app.loan_amount):,.0f}")
                    st.caption(app.loan_type.value)

                with col3:
                    status_color = "🟢" if app.status == ApplicationStatus.APPROVED else "🔴" if app.status == ApplicationStatus.REJECTED else "🟡"
                    st.write(f"{status_color} {app.status.value}")

                with col4:
                    confidence = evaluation.confidence_score if evaluation else "N/A"
                    st.write(f"Confidence: {confidence}")

                with col5:
                    if st.button("Details", key=f"view_{app.id}"):
                        st.session_state.selected_app_id = app.id
                        st.rerun()
    else:
        st.info("No applications found matching the criteria")

    db.close()

def render_application_details():
    """Render detailed application view"""
    st.header("Application Details")

    app_id = st.number_input("Enter Application ID", min_value=1, step=1)

    if st.button("Load Application"):
        db = DatabaseConnection.get_session()

        application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()

        if not application:
            st.error("Application not found")
            db.close()
            return

        applicant = db.query(Applicant).filter(Applicant.id == application.applicant_id).first()
        credit = db.query(CreditHistory).filter(CreditHistory.applicant_id == application.applicant_id).first()
        risk = db.query(RiskIndicators).filter(RiskIndicators.applicant_id == application.applicant_id).first()
        evaluation = db.query(ApplicationEvaluation).filter(ApplicationEvaluation.application_id == app_id).first()

        # Application details
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Evaluations", "Audit Trail", "Decision"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Applicant Information")
                st.write(f"**Name:** {applicant.first_name} {applicant.last_name}")
                st.write(f"**Email:** {applicant.email}")
                st.write(f"**Phone:** {applicant.phone}")
                st.write(f"**Annual Income:** ${float(applicant.annual_income):,.2f}")
                st.write(f"**Employment:** {applicant.employment_status.value}")

            with col2:
                st.subheader("Loan Details")
                st.write(f"**Amount:** ${float(application.loan_amount):,.2f}")
                st.write(f"**Type:** {application.loan_type.value}")
                st.write(f"**Purpose:** {application.loan_purpose}")
                st.write(f"**Term:** {application.loan_term_months} months")
                st.write(f"**Status:** {application.status.value}")

            if credit:
                st.subheader("Credit Information")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Credit Score", credit.credit_score)
                with col2:
                    st.metric("Credit Utilization", f"{float(credit.credit_utilization_percent):.1f}%")
                with col3:
                    st.metric("Accounts Open", credit.accounts_open)

        with tab2:
            st.subheader("Agent Evaluations")

            if evaluation:
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Credit Analysis Agent**")
                    if evaluation.credit_agent_result:
                        try:
                            credit_result = json.loads(evaluation.credit_agent_result)
                            st.json(credit_result)
                        except:
                            st.write(evaluation.credit_agent_result)

                with col2:
                    st.write("**Risk Assessment Agent**")
                    if evaluation.risk_agent_result:
                        try:
                            risk_result = json.loads(evaluation.risk_agent_result)
                            st.json(risk_result)
                        except:
                            st.write(evaluation.risk_agent_result)

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Compliance Agent**")
                    if evaluation.compliance_agent_result:
                        try:
                            compliance_result = json.loads(evaluation.compliance_agent_result)
                            st.json(compliance_result)
                        except:
                            st.write(evaluation.compliance_agent_result)

                with col2:
                    st.write("**Fraud Detection Agent**")
                    if evaluation.fraud_agent_result:
                        try:
                            fraud_result = json.loads(evaluation.fraud_agent_result)
                            st.json(fraud_result)
                        except:
                            st.write(evaluation.fraud_agent_result)
            else:
                st.info("No evaluation available")

        with tab3:
            st.subheader("Audit Trail")

            audits = db.query(AuditLog).filter(AuditLog.application_id == app_id).all()

            if audits:
                for audit in audits:
                    with st.container(border=True):
                        st.write(f"**{audit.agent_name}** - {audit.created_at}")
                        st.write(f"*{audit.action}*")
                        if audit.details:
                            try:
                                details = json.loads(audit.details)
                                st.json(details)
                            except:
                                st.write(audit.details)
            else:
                st.info("No audit records")

        with tab4:
            if evaluation:
                st.subheader("Final Decision")

                col1, col2, col3 = st.columns(3)

                with col1:
                    decision_icon = "✅" if evaluation.final_classification == Classification.APPROVED else "❌" if evaluation.final_classification == Classification.REJECTED else "⏳"
                    st.metric("Decision", f"{decision_icon} {evaluation.final_classification.value}")

                with col2:
                    st.metric("Confidence", f"{float(evaluation.confidence_score):.1%}")

                with col3:
                    st.metric("Evaluated", evaluation.evaluated_at.strftime("%Y-%m-%d %H:%M"))

                st.write("**Justification:**")
                st.write(evaluation.decision_justification)
            else:
                st.info("Application not yet evaluated")

        db.close()

def render_analytics():
    """Render analytics dashboard"""
    st.header("Analytics & Reports")

    db = DatabaseConnection.get_session()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Approval Rate")
        total = db.query(LoanApplication).count()
        if total > 0:
            approved = db.query(LoanApplication).filter(
                LoanApplication.status == ApplicationStatus.APPROVED
            ).count()
            approval_rate = (approved / total) * 100
            st.metric("Approval Rate", f"{approval_rate:.1f}%", delta=f"{approved}/{total}")

    with col2:
        st.subheader("Distribution by Status")
        statuses = {}
        for status in ApplicationStatus:
            count = db.query(LoanApplication).filter(LoanApplication.status == status).count()
            if count > 0:
                statuses[status.value] = count

        if statuses:
            st.bar_chart(statuses)

    st.subheader("Average Loan Amounts")
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_approved = db.query(LoanApplication).filter(
            LoanApplication.status == ApplicationStatus.APPROVED
        ).with_entities(LoanApplication.loan_amount).all()
        if avg_approved:
            avg = sum([float(app[0]) for app in avg_approved]) / len(avg_approved)
            st.metric("Avg Approved Loan", f"${avg:,.0f}")

    with col2:
        avg_rejected = db.query(LoanApplication).filter(
            LoanApplication.status == ApplicationStatus.REJECTED
        ).with_entities(LoanApplication.loan_amount).all()
        if avg_rejected:
            avg = sum([float(app[0]) for app in avg_rejected]) / len(avg_rejected)
            st.metric("Avg Rejected Loan", f"${avg:,.0f}")

    with col3:
        all_avg = db.query(LoanApplication).with_entities(LoanApplication.loan_amount).all()
        if all_avg:
            avg = sum([float(app[0]) for app in all_avg]) / len(all_avg)
            st.metric("Overall Avg Loan", f"${avg:,.0f}")

    db.close()

# Main app logic
if page == "Dashboard":
    render_dashboard()
elif page == "Submit Application":
    render_submit_application()
elif page == "View Applications":
    render_view_applications()
elif page == "Application Details":
    render_application_details()
elif page == "Analytics":
    render_analytics()

st.sidebar.divider()
st.sidebar.caption("🚀 Multi-Agent Loan Application Analysis System")
st.sidebar.caption(f"© 2024 - Using Claude AI")
