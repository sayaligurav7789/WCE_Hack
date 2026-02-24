from src.rag_pipeline import answer_question

while True:
    question = input("\nEnter question (or type exit): ")

    if question.lower() == "exit":
        break

    answer, context, sections, pages = answer_question(question)

    print("\nAnswer:\n", answer)
    print("\nSections:", sections)
    print("Pages:", pages)