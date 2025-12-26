import streamlit as st
import os
from pathlib import Path
from src.tools.pdf_processor import LeaseDocumentProcessor
from src.tools.embeddings import VectorStoreManager
from src.agents.supervisor import run_analysis

# Page config
st.set_page_config(
    page_title="LeaseLogic - AI Lease Analysis",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'lease_uploaded' not in st.session_state:
    st.session_state.lease_uploaded = False
if 'collection_name' not in st.session_state:
    st.session_state.collection_name = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Title and description
st.title("📜 LeaseLogic")
st.markdown("""
AI-powered lease analysis using multi-agent reasoning and California tenant law.

**How it works:**
1. Upload your lease PDF
2. Select your state
3. Ask questions about your lease
4. Get analysis comparing your lease terms vs. state law
""")

# Sidebar - Lease Upload
with st.sidebar:
    st.header("🏠 Your Lease")

    # State selection
    state_location = st.selectbox(
        "Select Your State",
        ["california", "new_york", "texas", "florida"],
        index=0,
        help="Currently optimized for California law"
    )

    # PDF Upload
    uploaded_file = st.file_uploader(
        "Upload Your Lease (PDF)",
        type=['pdf'],
        help="Upload your residential lease agreement"
    )

    if uploaded_file:
        if not st.session_state.lease_uploaded or st.session_state.collection_name is None:
            with st.spinner("[Lease] Processing your lease..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = Path("temp_lease.pdf")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    # Process PDF
                    processor = LeaseDocumentProcessor()
                    chunks = processor.process_lease_pdf(str(temp_path))

                    st.success(f"[OK] Processed {len(chunks)} chunks")

                    # Create vector store
                    collection_name = f"user_lease_{uploaded_file.name.replace('.pdf', '').replace(' ', '_')}"
                    vsm = VectorStoreManager()
                    vsm.create_lease_vectorstore(chunks, collection_name)

                    # Update session state
                    st.session_state.lease_uploaded = True
                    st.session_state.collection_name = collection_name

                    # Clean up
                    temp_path.unlink()

                    st.success(f"[OK] Lease indexed!")
                    st.info(f"Collection: `{collection_name}`")

                except Exception as e:
                    st.error(f"[ERROR] Error processing lease: {e}")
        else:
            st.success(f"[OK] Lease loaded: `{st.session_state.collection_name}`")
            if st.button("Upload Different Lease"):
                st.session_state.lease_uploaded = False
                st.session_state.collection_name = None
                st.session_state.chat_history = []
                st.rerun()

    st.markdown("---")
    st.caption("LeaseLogic v1.0 | Multi-Agent RAG System")

# Main area - Q&A Interface
if st.session_state.lease_uploaded:
    st.header("💬 Ask About Your Lease")

    # Display chat history
    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(entry['question'])
        with st.chat_message("assistant"):
            st.markdown(entry['answer'])

            # Show metadata in expander
            with st.expander("[Analysis] Analysis Details"):
                # Classification info (if available)
                if 'query_scope' in entry['metadata']:
                    scope_emoji = {
                        "lease_only": "[Lease]",
                        "law_only": "[Law Agent]",
                        "both": "[Both]"
                    }
                    st.info(f"{scope_emoji.get(entry['metadata']['query_scope'], '[Both]')} **Scope:** {entry['metadata']['query_scope'].replace('_', ' ').title()}")
                    if 'classification_reasoning' in entry['metadata']:
                        st.caption(f"Reasoning: {entry['metadata']['classification_reasoning']}")
                    st.markdown("---")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", entry['metadata']['confidence'])
                with col2:
                    st.metric("Quality Grade", f"{entry['metadata']['quality_grade']}/10")
                with col3:
                    st.metric("Iterations", entry['metadata']['iterations'])
                with col4:
                    if entry['metadata'].get('query_scope') in ["lease_only", "both", None]:
                        st.metric("Lease Score", f"{entry['metadata']['lease_score']:.2f}")
                    else:
                        st.metric("Lease Score", "N/A")

                if entry['metadata'].get('query_scope') in ["law_only", "both", None]:
                    st.caption(f"Law Score: {entry['metadata']['law_score']:.2f}")
                else:
                    st.caption("Law Score: N/A")

    # Question input
    user_question = st.chat_input("Ask a question about your lease...")

    if user_question:
        # Show user message
        with st.chat_message("user"):
            st.write(user_question)

        # Run analysis
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing..."):
                try:
                    # Run multi-agent analysis
                    result = run_analysis(
                        user_query=user_question,
                        lease_collection_name=st.session_state.collection_name,
                        state_location=state_location
                    )

                    # Display answer
                    st.markdown(result['final_answer'])

                    # Extract metadata
                    metadata = {
                        'confidence': result.get('confidence', 'UNKNOWN'),
                        'quality_grade': result.get('retrieval_quality_grade', 0),
                        'iterations': result.get('requery_count', 0) + 1,
                        'lease_score': result.get('lease_retrieval_score', 0),
                        'law_score': result.get('law_retrieval_score', 0),
                        'query_scope': result.get('query_scope', 'both'),
                        'classification_reasoning': result.get('classification_reasoning', 'N/A')
                    }

                    # Show metadata
                    with st.expander("[Analysis] Analysis Details"):
                        # Classification info
                        st.subheader("[Classifier] Query Classification")
                        scope_emoji = {
                            "lease_only": "[Lease]",
                            "law_only": "[Law Agent]",
                            "both": "[Both]"
                        }
                        st.info(f"{scope_emoji.get(metadata['query_scope'], '[Both]')} **Scope:** {metadata['query_scope'].replace('_', ' ').title()}")
                        st.caption(f"Reasoning: {metadata['classification_reasoning']}")

                        st.markdown("---")

                        # Performance metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Confidence", metadata['confidence'])
                        with col2:
                            st.metric("Quality Grade", f"{metadata['quality_grade']}/10")
                        with col3:
                            st.metric("Iterations", metadata['iterations'])
                        with col4:
                            if metadata['query_scope'] in ["lease_only", "both"]:
                                st.metric("Lease Score", f"{metadata['lease_score']:.2f}")
                            else:
                                st.metric("Lease Score", "N/A")

                        if metadata['query_scope'] in ["law_only", "both"]:
                            st.caption(f"Law Score: {metadata['law_score']:.2f}")
                        else:
                            st.caption("Law Score: N/A")

                        # Show findings
                        if st.checkbox("Show Detailed Findings"):
                            if metadata['query_scope'] in ["lease_only", "both"]:
                                st.subheader("[Lease] Lease Finding")
                                st.write(result.get('lease_finding', 'N/A'))

                            if metadata['query_scope'] in ["law_only", "both"]:
                                st.subheader("[Law Agent] Law Finding")
                                st.write(result.get('law_finding', 'N/A'))

                    # Add to chat history
                    st.session_state.chat_history.append({
                        'question': user_question,
                        'answer': result['final_answer'],
                        'metadata': metadata
                    })

                except Exception as e:
                    st.error(f"[ERROR] Error: {e}")
                    st.exception(e)

else:
    # Welcome screen
    st.info("👈 Upload your lease PDF in the sidebar to get started")

    st.subheader("Example Questions")
    st.markdown("""
    - Can my landlord charge a $300 late fee?
    - How much notice does my landlord need to give before entering?
    - What is the maximum security deposit allowed?
    - Can I break my lease early if I get a new job?
    - Is my landlord required to provide air conditioning?
    """)

    st.subheader("Features")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **[Classifier] Multi-Agent Analysis**
        - Lease document search
        - State law research
        - Quality verification
        - Answer synthesis
        """)
    with col2:
        st.markdown("""
        **[Law Agent] Legal Intelligence**
        - California tenant law database
        - Federal housing law coverage
        - Conflict detection
        - Plain-language explanations
        """)