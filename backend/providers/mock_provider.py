import asyncio
import time
from typing import Optional
from providers.base import LLMProvider, LLMResponse

# Benchmark pre-configured knowledge bases for realistic multi-model hallucination testing
BENCHMARK_RESPONSES = {
    "taj mahal": {
        "gpt": "The Taj Mahal was commissioned in 1632 by Mughal Emperor Shah Jahan to house the tomb of his favorite wife, Mumtaz Mahal. It is located in Delhi, India, and was designed by Ustad Ahmad Lahori. Construction was completed around 1648.",
        "gemini": "The Taj Mahal is an ivory-white marble mausoleum on the south bank of the Yamuna river in Agra, Uttar Pradesh, India. It was commissioned in 1631 by Mughal Emperor Shah Jahan and completed in 1648 (with surrounding complex finished in 1653). Its chief architect was Ustad Ahmad Lahori.",
        "claude": "The Taj Mahal is located in Agra, India. It was commissioned by Emperor Shah Jahan in 1631 and completed around 1653. However, some sources incorrectly claim it is in Delhi. The chief architect was Ustad Ahmad Lahori."
    },
    "iphone": {
        "gpt": "The original iPhone was officially unveiled by Steve Jobs on January 9, 2007, and released for sale in the United States on June 29, 2007. It introduced multi-touch interface and iOS.",
        "gemini": "The first iPhone was announced by Apple CEO Steve Jobs on January 9, 2007, and released to the public on June 29, 2007. It transformed the smartphone industry with its capacitive touchscreen.",
        "claude": "The first iPhone was released in late 2006 following Apple's announcement at Macworld, with broader availability in early 2007. It featured 2G GSM connectivity and a 3.5-inch display."
    },
    "risc-v": {
        "gpt": "RISC-V is an open-standard Instruction Set Architecture (ISA) provided under open-source licenses, meaning anyone can design and manufacture RISC-V chips without paying royalties to ARM. It offers modularity and extensibility, but ARM currently maintains higher ecosystem maturity and software optimization.",
        "gemini": "The primary advantage of RISC-V over ARM is that RISC-V is an open and royalty-free standard, avoiding proprietary vendor lock-in. It allows custom extensions without architectural license penalties. ARM, conversely, dominates with mature compiler toolchains, broad developer support, and validated silicon efficiency in mobile and data center.",
        "claude": "Key advantages of RISC-V include zero licensing fees, open architectural governance via RISC-V International, custom extension flexibility, and academic transparency. ARM requires costly architectural licenses, though ARM has decades of hardware-software co-optimization and widespread production deployment."
    },
    "nuclear": {
        "gpt": "Per unit of electricity generated (TWh), nuclear energy is among the safest energy sources, with death rates comparable to or lower than wind and solar, and orders of magnitude lower than coal, oil, and gas, which cause millions of deaths annually from air pollution.",
        "gemini": "Empirical studies, including data from Our World in Data and the World Health Organization, show that nuclear power causes approximately 0.03 deaths per terawatt-hour, compared to 24.6 deaths per TWh for coal and 18.4 for oil, making nuclear drastically safer than fossil fuels.",
        "claude": "Nuclear energy causes far fewer fatalities per TWh than fossil fuels due to negligible particulate air pollution during operation. The primary public concerns involve radioactive waste disposal and low-probability, high-consequence catastrophic accidents (e.g. Chernobyl, Fukushima)."
    }
}

class MockLLMProvider(LLMProvider):
    """
    High-fidelity Multi-Model Simulation Provider for testing, demonstrations,
    and offline academic benchmark evaluation without burning API credits.
    """
    def __init__(self, persona: str = "gpt", model: Optional[str] = None):
        super().__init__(api_key="simulated_key", model=model or f"simulated-{persona}")
        self.persona = persona.lower()

    def provider_name(self) -> str:
        names = {
            "gpt": "OpenAI (Simulated)",
            "gemini": "Google Gemini (Simulated)",
            "claude": "Anthropic Claude (Simulated)",
            "groq": "Groq LLaMA (Simulated)"
        }
        return names.get(self.persona, f"Model-{self.persona.upper()}")

    def model_name(self) -> str:
        return self._model

    def is_configured(self) -> bool:
        return True

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> LLMResponse:
        start_time = time.perf_counter()
        await asyncio.sleep(0.35)  # Simulate network latency

        prompt_lower = prompt.lower()
        matched_content = None

        for key, responses in BENCHMARK_RESPONSES.items():
            if key in prompt_lower:
                matched_content = responses.get(self.persona, responses.get("gpt"))
                break

        if not matched_content:
            # Dynamic synthesized answer reflecting persona perspective
            if "gpt" in self.persona:
                matched_content = f"Regarding '{prompt}': Research shows that the primary factual considerations involve historical consensus, empirical measurements, and peer-reviewed documentation. Key factors include verified institutional records and official timeline corroboration."
            elif "gemini" in self.persona:
                matched_content = f"Addressing '{prompt}': From an analytical standpoint, key data sources and encyclopedic records indicate documented milestones. Verification against primary sources shows consistent evidentiary patterns across verified literature."
            else:
                matched_content = f"In analysis of '{prompt}': Multiple perspectives exist across historical reporting. While core aspects are documented in academic registries, specific secondary claims occasionally feature documented discrepancies in public discourse."

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return LLMResponse(
            provider_name=self.provider_name(),
            model_name=self.model_name(),
            content=matched_content,
            latency_ms=round(elapsed_ms, 2),
            token_count=len(matched_content.split()) * 2,
            status="success",
            metadata={"simulated": True}
        )
