from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    {
        "id": "eval_1",
        "domain": "History & Architecture",
        "question": "Where is the Taj Mahal located, who commissioned it, and when was it completed?",
        "ground_truth_answer": "The Taj Mahal is located in Agra, Uttar Pradesh, India. It was commissioned by Mughal Emperor Shah Jahan in 1631/1632 in memory of Mumtaz Mahal and its main mausoleum was finished around 1648.",
        "claims": [
            {
                "claim": "The Taj Mahal is located in Agra, Uttar Pradesh, India.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "The Taj Mahal was commissioned by Shah Jahan.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "The Taj Mahal is located in Delhi.",
                "expected_status": "CONTRADICTED",
                "is_hallucination": True
            },
            {
                "claim": "The Taj Mahal was designed by Ustad Ahmad Lahori.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            }
        ]
    },
    {
        "id": "eval_2",
        "domain": "Technology & Consumer Electronics",
        "question": "When was the original Apple iPhone officially released for sale to the public?",
        "ground_truth_answer": "The original iPhone was announced on January 9, 2007, and released for sale in the United States on June 29, 2007.",
        "claims": [
            {
                "claim": "The original iPhone was released for sale in June 2007.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "The first iPhone was released in late 2006.",
                "expected_status": "CONTRADICTED",
                "is_hallucination": True
            },
            {
                "claim": "The iPhone was announced by Steve Jobs.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            }
        ]
    },
    {
        "id": "eval_3",
        "domain": "Computer Architecture",
        "question": "What is the primary licensing model difference between RISC-V and ARM?",
        "ground_truth_answer": "RISC-V is an open-standard and royalty-free instruction set architecture, whereas ARM ISAs and IP cores require commercial licensing fees and royalties.",
        "claims": [
            {
                "claim": "RISC-V is an open and royalty-free standard ISA.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "ARM requires commercial licenses and ongoing royalties.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "RISC-V requires developers to pay licensing royalties to ARM Holdings.",
                "expected_status": "CONTRADICTED",
                "is_hallucination": True
            }
        ]
    },
    {
        "id": "eval_4",
        "domain": "Energy & Environmental Science",
        "question": "How does the mortality rate per TWh of nuclear energy compare with fossil fuel sources?",
        "ground_truth_answer": "Nuclear power causes substantially fewer deaths per TWh generated (approx 0.03 to 0.07 deaths/TWh) than coal (24.6 deaths/TWh) or oil (18.4 deaths/TWh).",
        "claims": [
            {
                "claim": "Nuclear energy results in far fewer deaths per terawatt-hour than coal or oil.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "Coal combustion causes significant fatalities predominantly from fine particulate air pollution.",
                "expected_status": "SUPPORTED",
                "is_hallucination": False
            },
            {
                "claim": "Nuclear energy causes more deaths per TWh of electricity produced than coal power.",
                "expected_status": "CONTRADICTED",
                "is_hallucination": True
            }
        ]
    }
]
