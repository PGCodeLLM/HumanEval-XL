#!/usr/bin/env python3
"""
Prepare HumanEval-XL dataset for inference by adding completion instructions and converting format
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def load_problems(data_file: Path) -> List[Dict[str, Any]]:
    """Load problems from a JSONL file"""
    problems = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                problems.append(json.loads(line))
    return problems

def get_completion_instruction_map() -> Dict[str, str]:
    """
    Returns a mapping from natural language to corresponding completion instruction.
    The instruction guides the model to complete only the method body without extra code.
    """
    return {
        "English": "Complete the body of the method below. Do not add imports, classes, or extra braces.\n",
        "Chinese": "完成下面方法的主体部分。不要添加导入语句、类或额外的大括号。\n",
        "Russian": "Завершите тело метода ниже. Не добавляйте импорты, классы или лишние скобки.\n",
        "German": "Vervollständigen Sie den Körper der unten stehenden Methode. Fügen Sie keine Importe, Klassen oder zusätzliche Klammern hinzu.\n",
        "Spanish": "Complete el cuerpo del método a continuación. No agregue importaciones, clases o llaves adicionales.\n",
        "French": "Complétez le corps de la méthode ci-dessous. N'ajoutez pas d'importations, de classes ou d'accolades supplémentaires.\n",
        "Italian": "Completa il corpo del metodo qui sotto. Non aggiungere importazioni, classi o parentesi graffe aggiuntive.\n",
        "Portuguese": "Complete o corpo do método abaixo. Não adicione importações, classes ou chaves adicionais.\n",
        "Greek": "Συμπληρώστε το σώμα της παρακάτω μεθόδου. Μην προσθέτετε εισαγωγές, κλάσεις ή επιπλέον αγκύλες.\n",
        "Hungarian": "Töltse ki az alábbi metódus törzsét. Ne adjon hozzá importokat, osztályokat vagy extra kapcsos zárójeleket.\n",
        "Dutch": "Voltooi de hoofdtekst van de onderstaande methode. Voeg geen imports, klassen of extra accolades toe.\n",
        "Finnish": "Täydennä alla olevan metodin runko. Älä lisää tuonteja, luokkia tai ylimääräisiä aaltosulkeita.\n",
        "Indonesian": "Lengkapi isi metode di bawah ini. Jangan menambahkan impor, kelas, atau tanda kurung kurawal tambahan.\n",
        "Turkish": "Aşağıdaki metodun gövdesini tamamlayın. İçe aktarma, sınıf veya ekstra parantez eklemeyin.\n",
        "Arabic": "أكمل محتوى الدالة أدناه. لا تضف استيرادات أو فئات أو أقواس إضافية.\n",
        "Vietnamese": "Hoàn thành nội dung của phương thức bên dưới. Không thêm import, class hoặc dấu ngoặc nhọn thừa.\n",
        "Bulgarian": "Попълнете тялото на метода по-долу. Не добавяйте импорти, класове или допълнителни скоби.\n",
        "Persian": "بدنه متد زیر را تکمیل کنید. وارد کردن، کلاس یا براکت اضافی اضافه نکنید.\n",
        "Malay": "Lengkapkan badan kaedah di bawah. Jangan tambah import, kelas, atau kurungan dakap tambahan.\n",
        "Hebrew": "השלם את גוף המתודה למטה. אל תוסיף ייבואים, מחלקות או סוגריים מסולסלים נוספים.\n",
        "Estonian": "Täitke alloleva meetodi keha. Ärge lisage importi, klasse ega lisasulge.\n",
        "Tagalog": "Kumpletuhin ang katawan ng pamamaraan sa ibaba. Huwag magdagdag ng mga import, klase, o karagdagang braces.\n",
        "Afrikaans": "Voltooi die liggaam van die metode hieronder. Moenie invoere, klasse of ekstra hakies byvoeg nie.\n",
    }

def prepare_for_inference(problems: List[Dict[str, Any]], natural_language: str = "English") -> List[Dict[str, Any]]:
    """
    Prompt to generate uncompleted part only.

    Args:
        problems: List of problems to prepare
        natural_language: Natural language for the completion instruction
    """
    inference_data = []

    # Get language-specific instruction
    instruction_map = get_completion_instruction_map()
    completion_instruction = instruction_map.get(natural_language, instruction_map["English"])

    for problem in problems:
        # Add completion instruction to the beginning of the prompt
        enhanced_prompt = completion_instruction + problem["prompt"]

        # Convert to eval-cli format with 'prompt' key (matching the run script)
        inference_item = {
            "task_id": problem["task_id"],
            "prompt": enhanced_prompt,  # Use 'prompt' key to match run script
            "language": problem["language"],
            "natural_language": problem["natural_language"],
            "entry_point": problem["entry_point"],
            "test": problem["test"],
            "canonical_solution": problem.get("canonical_solution", "")
        }
        inference_data.append(inference_item)

    return inference_data

def main():
    parser = argparse.ArgumentParser(description="Prepare HumanEval-XL dataset for inference")
    parser.add_argument("--programming_language", type=str, required=True,
                       choices=["python", "java", "javascript", "typescript", "go", "csharp",
                               "php", "ruby", "kotlin", "scala", "swift", "perl"],
                       help="Programming language")
    parser.add_argument("--natural_language", type=str, required=True,
                       choices=["English", "Russian", "Chinese", "German", "Spanish", "French",
                               "Italian", "Portuguese", "Greek", "Hungarian", "Dutch", "Finnish",
                               "Indonesian", "Turkish", "Arabic", "Vietnamese", "Bulgarian",
                               "Persian", "Malay", "Hebrew", "Estonian", "Tagalog", "Afrikaans"],
                       help="Natural language")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="Output directory for processed dataset")

    args = parser.parse_args()

    # Find the data file
    script_dir = Path(__file__).parent
    data_file = script_dir / "data" / args.programming_language / f"{args.natural_language}.jsonl"

    if not data_file.exists():
        print(f"Error: Data file not found: {data_file}")
        return 1

    print(f"Loading problems from: {data_file}")
    problems = load_problems(data_file)
    print(f"Loaded {len(problems)} problems")

    # Prepare for inference with language-specific instruction
    inference_data = prepare_for_inference(problems, natural_language=args.natural_language)

    # Write output to centralized location with directory structure
    output_dir = Path(args.output_dir)
    prog_lang_dir = output_dir / args.programming_language
    prog_lang_dir.mkdir(parents=True, exist_ok=True)

    output_path = prog_lang_dir / f"{args.natural_language}.jsonl"

    with open(output_path, 'w', encoding='utf-8') as f:
        for item in inference_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Dataset prepared for inference: {output_path}")
    print(f"Total items: {len(inference_data)}")
    print(f"Enhanced prompts with completion instruction added")

    return 0

if __name__ == "__main__":
    exit(main())
