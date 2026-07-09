"""Interactive Streamlit demo for HelixAgent.

This entry point is intentionally self-contained so it can be deployed directly
from the repository root on Streamlit Community Cloud.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import streamlit as st

from agent.agent_core import AgenticAssistant, cosine_sim


@dataclass(frozen=True)
class DemoExample:
    """Preset prompt shown in the demo sidebar."""

    label: str
    prompt: str


EXAMPLES = (
    DemoExample(
        "System summary",
        "Summarize the current HelixAgent architecture and explain its main engineering strengths.",
    ),
    DemoExample(
        "Vector workflow",
        "Compare vectors and explain why cosine similarity is useful in AI systems.",
    ),
    DemoExample(
        "Web-assisted plan",
        "Search the web for recent MLOps reliability practices and produce a concise implementation plan.",
    ),
)


@st.cache_resource(show_spinner=False)
def get_assistant() -> AgenticAssistant:
    """Create one reusable agent instance per Streamlit session process."""

    return AgenticAssistant()


def render_sidebar() -> None:
    """Render architecture, capability, and example-prompt controls."""

    with st.sidebar:
        st.title("🧬 HelixAgent")
        st.caption("Autonomous MLOps & multi-agent infrastructure demo")

        st.subheader("Capabilities")
        st.markdown(
            """
- LangGraph workflow orchestration
- Python fallback planner
- Optional Java planner integration
- Optional C++ vector acceleration
- FastAPI service layer
- CI/CD and supply-chain security
"""
        )

        st.subheader("Try an example")
        for example in EXAMPLES:
            if st.button(example.label, use_container_width=True):
                st.session_state["prompt"] = example.prompt

        st.divider()
        st.markdown(
            "[View the source on GitHub](https://github.com/CoreyLeath-code/HelixAgent)"
        )
        st.caption(
            "The public demo uses built-in fallback behavior when optional native or external services are unavailable."
        )


def render_metrics() -> None:
    """Show concise implementation details at the top of the page."""

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("API", "FastAPI")
    col2.metric("Orchestration", "LangGraph")
    col3.metric("Runtime", "Python 3.11")
    col4.metric("Deployment", "Streamlit")


def render_architecture() -> None:
    """Render a lightweight architecture diagram without external assets."""

    with st.expander("Architecture overview"):
        st.mermaid(
            """
flowchart LR
    U[User] --> S[Streamlit Demo]
    S --> A[HelixAgent Orchestrator]
    A --> P[Planner]
    A --> V[Vector Utility]
    A --> W[Web Search Tool]
    P --> R[Response]
    V --> R
    W --> R
"""
        )


def render_vector_lab() -> None:
    """Expose the vector utility as a transparent, deterministic mini-demo."""

    with st.expander("Vector similarity lab"):
        st.write("Compare two three-dimensional vectors using HelixAgent's cosine utility.")
        left = st.text_input("Vector A", "1, 0, 1")
        right = st.text_input("Vector B", "0.5, 0, 0.5")

        if st.button("Calculate similarity"):
            try:
                vector_a = [float(value.strip()) for value in left.split(",")]
                vector_b = [float(value.strip()) for value in right.split(",")]
                if len(vector_a) != len(vector_b) or not vector_a:
                    raise ValueError("Vectors must be non-empty and have equal dimensions.")
                score = cosine_sim(vector_a, vector_b)
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(f"Cosine similarity: {score:.4f}")


def run_agent(prompt: str) -> tuple[str, float]:
    """Run the agent and return its response with elapsed time."""

    started = time.perf_counter()
    response = get_assistant().run(prompt)
    elapsed = time.perf_counter() - started
    return response, elapsed


def main() -> None:
    """Render the HelixAgent Streamlit application."""

    st.set_page_config(
        page_title="HelixAgent Demo",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    render_sidebar()

    st.title("🧬 HelixAgent")
    st.subheader("Enterprise multi-agent AI orchestration demo")
    st.write(
        "Explore HelixAgent's planning, orchestration, fallback execution, and vector-processing capabilities through an interactive interface."
    )

    render_metrics()
    render_architecture()

    prompt = st.text_area(
        "Ask HelixAgent",
        key="prompt",
        height=140,
        placeholder="Example: Compare vectors and then draft an implementation summary.",
    )

    run_clicked = st.button("Run HelixAgent", type="primary", use_container_width=True)
    if run_clicked:
        if not prompt.strip():
            st.warning("Enter a prompt before running the agent.")
        else:
            with st.spinner("Planning and executing the workflow..."):
                try:
                    response, elapsed = run_agent(prompt.strip())
                except Exception as exc:  # pragma: no cover - defensive UI boundary
                    st.error("HelixAgent could not complete this request.")
                    st.exception(exc)
                else:
                    st.subheader("Agent response")
                    st.code(response, language="text")
                    st.caption(f"Completed in {elapsed:.3f} seconds")

    render_vector_lab()

    st.divider()
    st.caption(
        "Portfolio demonstration by Corey Leath · Built with Streamlit, FastAPI, LangGraph, Python, and optional native integrations."
    )


if __name__ == "__main__":
    main()
