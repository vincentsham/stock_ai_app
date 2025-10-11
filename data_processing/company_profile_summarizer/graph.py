from langgraph.graph import StateGraph, START, END
from states import CompanyProfileState
from nodes import summarize_company_profile
import json


def create_graph() -> StateGraph:
    """
    Creates a simple StateGraph for company profile summarization.
    The graph has a single node: summarize_company_profile.
    """
    graph = StateGraph(CompanyProfileState)
    graph.add_node("summarize", summarize_company_profile)
    graph.add_edge(START, "summarize")
    graph.add_edge("summarize", END)
    return graph

# Example usage (uncomment for testing):
if __name__ == "__main__":
    state = CompanyProfileState(
        tic="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        country="USA",
        market_cap="2.5T",
        employees=150000,
        exchange="NASDAQ",
        currency="USD",
        website="https://apple.com",
        description=(
            "Apple Inc. is a globally renowned technology company headquartered in Cupertino, California, United States. "
            "Founded in 1976 by Steve Jobs, Steve Wozniak, and Ronald Wayne, Apple has grown to become one of the world’s most valuable and influential corporations, recognized for its innovation, design excellence, and ecosystem integration. "
            "The company designs, manufactures, and markets a wide range of consumer electronics, software, and services, with a primary focus on delivering seamless user experiences across its product portfolio. "
            "Apple’s flagship product is the iPhone, a line of smartphones that has revolutionized the mobile industry since its introduction in 2007. The iPhone is known for its advanced hardware, proprietary iOS operating system, and integration with Apple’s ecosystem of services and devices. "
            "In addition to the iPhone, Apple produces the iPad, a leading tablet device used in education, business, and personal entertainment, and the Mac family of personal computers, which includes the MacBook Air, MacBook Pro, iMac, Mac mini, and Mac Studio. These products are recognized for their performance, build quality, and macOS software. "
            "The company’s wearable and accessories segment includes the Apple Watch, a market-leading smartwatch with health, fitness, and connectivity features, and AirPods, wireless earbuds that have become a cultural phenomenon. Apple also offers the HomePod smart speaker and a variety of accessories such as keyboards, cases, and chargers. "
            "The company’s services business has grown rapidly, encompassing the App Store, Apple Music, Apple TV+, Apple Arcade, iCloud, Apple Pay, and AppleCare. These services provide recurring revenue streams and deepen customer engagement within the Apple ecosystem. "
            "Apple operates a global retail network, both online and through physical Apple Stores, which are known for their distinctive architecture, customer service, and hands-on product experiences. The company’s supply chain is highly sophisticated, with manufacturing partners and suppliers located around the world, enabling Apple to deliver products at scale while maintaining high standards for quality and sustainability. "
            "Apple’s business model emphasizes vertical integration, controlling both hardware and software to optimize performance, security, and user experience. The company invests heavily in research and development, focusing on areas such as artificial intelligence, augmented reality, custom silicon (including the M-series chips), and environmental initiatives. Apple is committed to privacy and data security, positioning itself as a leader in protecting user information. "
            "With a diverse customer base spanning consumers, businesses, educational institutions, and creative professionals, Apple continues to expand its presence in key markets across the Americas, Europe, Greater China, Japan, and the rest of Asia Pacific. The company’s brand is synonymous with innovation, quality, and design, and its products and services are used by hundreds of millions of people worldwide."
        )
    )
    graph = create_graph()
    app = graph.compile()
    result = app.invoke(state)
    result = dict(result)
    print(json.dumps(result, indent=2))

    # Count how many words in description, summary and short_summary
    description_word_count = len(result.get("description", "").split())
    summary_word_count = len(result.get("summary", "").split())
    short_summary_word_count = len(result.get("short_summary", "").split())
    print(f"Description word count: {description_word_count}")
    print(f"Summary word count: {summary_word_count}")
    print(f"Short summary word count: {short_summary_word_count}")

