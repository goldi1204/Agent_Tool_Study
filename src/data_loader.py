# src/data_loader.py
from datasets import load_dataset
import random

def get_hf_hotpotqa_dataset(num_samples=10, seed=42):
    """
    Hugging Face에서 HotpotQA 데이터셋을 로드하여 실험 포맷에 맞게 변환합니다.
    """
    random.seed(seed)
    
    # HotpotQA의 validation 셋 중 'distractor' 세팅 로드
    print("⏳ Downloading HotpotQA from Hugging Face...")
    dataset = load_dataset("hotpot_qa", 'distractor', split='validation')
    
    # 실험을 위해 지정된 개수만큼 샘플링
    sampled_indices = random.sample(range(len(dataset)), num_samples)
    sampled_data = dataset.select(sampled_indices)
    
    experiment_data = []
    
    for item in sampled_data:
        question_id = item['id']
        question = item['question']
        ground_truth = item['answer']
        
        # [데이터 오염 로직 구성]
        # 실제 연구에서는 LLM을 사용해 교묘한 오답(Distractor) 컨텍스트를 생성해야 하지만,
        # 여기서는 실험 통제를 위해 정답과 무관한 다른 문서나 변형된 문자열을 오답으로 주입합니다.
        # 예시: 정답 문자열을 뒤집거나, "정보 없음"으로 오염
        fake_distractor_answer = f"[Poisoned] {ground_truth[::-1]}" 
        
        # RAG 실험을 위한 컨텍스트(문서) 구성 (선택 사항)
        # HotpotQA는 여러 문서(context)를 제공하므로, 이를 조합하여 에이전트에게 줄 수 있습니다.
        
        experiment_data.append({
            "id": question_id,
            "text": question,
            "ground_truth": ground_truth,
            "distractor": fake_distractor_answer # 에이전트 A의 도구가 반환할 오염된 결과
        })
        
    print(f"✅ Successfully loaded {num_samples} samples from Hugging Face.")
    return experiment_data