import streamlit as st
import PyPDF2
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import faiss
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain_groq import ChatGroq
from rouge import Rouge


# Function to initialize conversation chain with GROQ language model
groq_api_key = ""

llm_groq=ChatGroq(model="llama3-8b-8192",
                  groq_api_key=groq_api_key)
# Streamlit app
st.set_page_config(page_title="DocDynamo", layout="wide")

st.title("DocDynamo🚀")
uploaded_file = st.file_uploader("Please upload a PDF file to begin!", type="pdf")

st.sidebar.title("DocDynamo By OpenRAG")
st.sidebar.markdown(
    """
    🌟 **Introducing DocDynamo by OpenRAG: Your PDF Companion!** 📚

Welcome, esteemed users, to the groundbreaking release of DocDynamo on May 21, 2024. At OpenRAG, we are committed to pioneering solutions for modern challenges, and DocDynamo is our latest triumph.

    """
    
)

st.sidebar.markdown(
    """
    💡 **How DocDynamo Works**

Simply upload your PDF, and let DocDynamo work its magic. Once processed, you can ask DocDynamo any question pertaining to the content of your PDF. It's like having a personal assistant at your fingertips, ready to provide instant answers.
    """
    
)

st.sidebar.markdown(
    """
    📧 **Get in Touch**

For inquiries or collaboration proposals, please don't hesitate to reach out to us:
📩 Email: openrag189@gmail.com
🔗 LinkedIn: [OpenRAG](https://www.linkedin.com/company/102036854/admin/dashboard/)
📸 Instagram: [OpenRAG](https://www.instagram.com/open.rag?igsh=MnFwMHd5cjU1OGFj)

Experience the future of PDF interaction with DocDynamo. Welcome to a new era of efficiency and productivity. OpenRAG: Empowering You Through Innovation. 🚀
    """
    
)
if uploaded_file:
    # Inform the user that processing has started
    with st.spinner(f"Processing `{uploaded_file.name}`..."):
        # Read the PDF file
        pdf = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=50)
        texts = text_splitter.split_text(pdf_text)

        # Create metadata for each chunk
        metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

        # Create a Chroma vector store
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': "cpu"})
        docsearch = faiss.from_documents(texts, embeddings, metadatas=metadatas)

        # Initialize message history for conversation
        message_history = ChatMessageHistory()

        # Memory for conversational context
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key="answer",
            chat_memory=message_history,
            return_messages=True,
        )

        # Create a chain that uses the Chroma vector store
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm_groq,
            chain_type="stuff",
            retriever=docsearch.as_retriever(),
            memory=memory,
            return_source_documents=True,
        )

    st.success(f"Processing `{uploaded_file.name}` done. You can now ask questions!")

    user_input = st.text_input("Ask a question about the PDF:")

    if user_input:
        # Call the chain with user's message content
        res = chain.invoke(user_input)
        answer = res["answer"]
        source_documents = res["source_documents"]

        text_elements = []  # Initialize list to store text elements

        # Process source documents if available
        if source_documents:
            for source_idx, source_doc in enumerate(source_documents):
                source_name = f"source_{source_idx}"
                # Create the text element referenced in the message
                text_elements.append(source_doc.page_content)
            source_names = [f"source_{idx}" for idx in range(len(source_documents))]

            # Add source references to the answer
            if source_names:
                answer += f"\nSources: {', '.join(source_names)}"
            else:
                answer += "\nNo sources found"

        # Display the results
        st.markdown(f"**Answer:** {answer}")

        for idx, element in enumerate(text_elements):
            with st.expander(f"Source {idx}"):
                st.write(element)




rouge = Rouge()  # Initialize ROUGE calculator

# Preprocess answer and reference summaries (replace with your preprocessing logic)
processed_answer = answer.lower().split()
reference_summaries = [summary.lower().split() for summary in reference_summaries_list]

# Calculate ROUGE scores and average them
scores = rouge.get_scores(processed_answer, reference_summaries, avg=True)
rouge_l_score = scores["rouge-l"]["f"]
rouge_n_score = scores["rouge-n"]["f"]

# Display ROUGE scores alongside the answer
st.markdown(f"**Answer:** {answer}")
st.write(f"ROUGE-L Score: {rouge_l_score:.4f}")
st.write(f"ROUGE-N Score: {rouge_n_score:.4f}")
