import gradio as gr
import markdown
import traceback

from ai_product_review_generator.agents import ReviewAgents
from ai_product_review_generator.generator import ProductReviewGenerator
from ai_product_review_generator.model import Model
from ai_product_review_generator.utils import custom_css, example_products, get_default_llm


def generate_review(llm_provider, llm_name, api_key, product_name):
    try:
        if not api_key:
            return gr.update(
                value="<p style='color: red;'>⚠️ Please enter your API key.</p>",
                visible=True,
            )
        if not llm_name or llm_name.strip() == "":
            return gr.update(
                value="<p style='color: red;'>⚠️ Please enter a model name.</p>",
                visible=True,
            )
        if not product_name or product_name.strip() == "":
            return gr.update(
                value="<p style='color: red;'>⚠️ Please enter a product name.</p>",
                visible=True,
            )

        # Build agents + generator
        llm = Model(llm_provider, llm_name, api_key)
        review_agents = ReviewAgents(llm)

        # NOTE: This matches the updated generator.py I gave you
        generate_product_review = ProductReviewGenerator(review_agents)

        product_review_stream = generate_product_review.run(product_name=product_name)

        final_output = ""
        for chunk in product_review_stream:
            # chunk is expected to be a string
            final_output += str(chunk)

        if not final_output.strip():
            return gr.update(
                value=(
                    "<p style='color: orange;'>⚠️ No review was generated. "
                    "This might be due to API rate limits or the product not being found. "
                    "Please try again or try a different product.</p>"
                ),
                visible=True,
            )

        html_body = markdown.markdown(final_output)
        html_content = f"<div>{html_body}</div>"

        return gr.update(value=html_content, visible=True)

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error occurred: {error_trace}")

        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
            return gr.update(
                value=(
                    "<p style='color: red;'>❌ <strong>API Key Error:</strong> "
                    "Your API key appears to be invalid or doesn't have access. "
                    "Please check your API key and try again.</p>"
                    f"<details><summary>Technical Details</summary><pre>{error_msg}</pre></details>"
                ),
                visible=True,
            )
        elif "rate" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg:
            return gr.update(
                value=(
                    "<p style='color: red;'>❌ <strong>Rate Limit/Quota Error:</strong> "
                    "You've exceeded your API rate limit or quota. Please wait and try again, "
                    "or check your account billing.</p>"
                    f"<details><summary>Technical Details</summary><pre>{error_msg}</pre></details>"
                ),
                visible=True,
            )
        elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
            return gr.update(
                value=(
                    "<p style='color: red;'>❌ <strong>Connection Error:</strong> "
                    "Could not connect to the API. Please check your internet connection and try again.</p>"
                    f"<details><summary>Technical Details</summary><pre>{error_msg}</pre></details>"
                ),
                visible=True,
            )
        else:
            return gr.update(
                value=(
                    f"<p style='color: red;'>❌ <strong>Error:</strong> {error_msg}</p>"
                    f"<details><summary>Full Error Trace</summary><pre>{error_trace}</pre></details>"
                ),
                visible=True,
            )


with gr.Blocks(title="Product Review Generator", css=custom_css) as demo:
    gr.Markdown("# AI Product Review Generator", elem_classes="center-text")
    gr.Markdown("Generate comprehensive, AI-powered product reviews using multiple LLM providers.")

    with gr.Row():
        with gr.Column(scale=1):
            llm_provider = gr.Radio(
                label="Select LLM Provider",
                choices=["OpenAI", "Gemini", "Claude", "Grok"],
                value="OpenAI",
            )

            def update_llm_name(provider):
                return get_default_llm(provider)

            llm_name = gr.Textbox(
                label="Enter LLM Name",
                value=get_default_llm("OpenAI"),
                info="Specify the model name based on the provider.",
            )
            llm_provider.change(fn=update_llm_name, inputs=llm_provider, outputs=llm_name)

            api_key = gr.Textbox(
                label="Enter API Key",
                type="password",
                placeholder="Enter your API key here...",
            )

            gr.Markdown("### Select or Enter Product")
            selected_prompt = gr.Radio(
                label="Example products:",
                choices=example_products,
                value=example_products[0],
            )
            product_input = gr.Textbox(
                label="Or enter your own product name",
                value=example_products[0],
                placeholder="e.g., iPhone 15 Pro Max",
            )
            generate_btn = gr.Button("🚀 Generate Review", variant="primary")

            gr.Markdown("---")
            gr.Markdown(
                """
            **Need an API Key?**
            - [OpenAI](https://platform.openai.com/api-keys)
            - [Google Gemini](https://aistudio.google.com/apikey)
            - [Anthropic Claude](https://console.anthropic.com/)
            - [xAI Grok](https://console.x.ai/)
            """
            )

        with gr.Column(scale=2):
            output = gr.HTML(
                label="Generated Review",
                value="<p style='color: gray; text-align: center; padding: 50px;'>Your review will appear here...</p>",
                visible=True,
            )

    def sync_product(selected, current):
        return selected

    selected_prompt.change(sync_product, [selected_prompt, product_input], product_input)

    generate_btn.click(
        generate_review,
        inputs=[llm_provider, llm_name, api_key, product_input],
        outputs=[output],
    )

demo.launch()

