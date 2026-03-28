import json
import os
from datetime import datetime
from typing import Dict, List

def format_debate_transcript(
    question_id,
    q_text,
    ground_truth,
    distractor,
    condition,
    tool_acc,
    tool_value,
    agent_responses,
    metrics,
    output_dir="results/transcripts"
):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/debate_q{question_id}_{condition}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"토론 기록 - Question #{question_id}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"실험 조건: {condition}\n")
        f.write(f"도구 정확도: {tool_acc}\n")
        f.write(f"도구 결과값: {tool_value}\n")
        f.write(f"정답: {ground_truth}\n")
        f.write(f"방해 요소(distractor): {distractor}\n\n")
        
        f.write("-"*80 + "\n")
        f.write("문제:\n")
        f.write("-"*80 + "\n")
        f.write(f"{q_text}\n\n")
        
        for round_num in range(1, 4):
            f.write("="*80 + "\n")
            f.write(f"Round {round_num}\n")
            f.write("="*80 + "\n\n")
            
            for agent_id in ["A", "B", "C"]:
                response = agent_responses[agent_id][round_num - 1]
                
                f.write(f"[Agent {agent_id}]\n")
                f.write("-"*80 + "\n")
                
                if response.get("tool_used", False):
                    f.write("🔧 도구 사용: 예\n")
                
                f.write(f"\n추론 과정:\n{response['reasoning']}\n\n")
                f.write(f"최종 답변: {response['answer']}\n")
                f.write(f"신뢰도: {response.get('confidence', 'N/A')}\n")
                f.write("-"*80 + "\n\n")
        
        f.write("="*80 + "\n")
        f.write("최종 결과\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Agent A 최종 답변: {metrics['agent_a_final_answer']}\n")
        f.write(f"Agent B 최종 답변: {metrics['agent_b_final_answer']}\n")
        f.write(f"Agent C 최종 답변: {metrics['agent_c_final_answer']}\n\n")
        
        f.write(f"Agent A 정답 여부: {'✅ 정답' if metrics['a_is_correct'] else '❌ 오답'}\n")
        f.write(f"Agent B 정답 여부: {'✅ 정답' if metrics['b_is_correct'] else '❌ 오답'}\n")
        f.write(f"Agent C 정답 여부: {'✅ 정답' if metrics['c_is_correct'] else '❌ 오답'}\n\n")
        
        f.write(f"설득 성공 여부 (is_persuaded): {'✅ 예' if metrics['is_persuaded'] else '❌ 아니오'}\n")
        f.write(f"도구 사용 횟수: {metrics['tool_used_count']}\n")
        f.write(f"반박 횟수: {metrics['challenge_count']}\n")
        
        f.write("\n" + "="*80 + "\n")
    
    return filename

def format_debate_json(
    question_id,
    q_text,
    ground_truth,
    distractor,
    condition,
    tool_acc,
    tool_value,
    agent_responses,
    metrics,
    output_dir="results/transcripts"
):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/debate_q{question_id}_{condition}_{timestamp}.json"
    
    data = {
        "metadata": {
            "question_id": question_id,
            "condition": condition,
            "tool_accuracy": tool_acc,
            "tool_result_value": tool_value,
            "ground_truth": ground_truth,
            "distractor": distractor,
            "timestamp": timestamp
        },
        "question": {
            "text": q_text
        },
        "debate_rounds": [],
        "final_results": {
            "answers": {
                "agent_a": metrics['agent_a_final_answer'],
                "agent_b": metrics['agent_b_final_answer'],
                "agent_c": metrics['agent_c_final_answer']
            },
            "correctness": {
                "agent_a": bool(metrics['a_is_correct']),
                "agent_b": bool(metrics['b_is_correct']),
                "agent_c": bool(metrics['c_is_correct'])
            },
            "metrics": {
                "is_persuaded": bool(metrics['is_persuaded']),
                "tool_used_count": metrics['tool_used_count'],
                "challenge_count": metrics['challenge_count']
            }
        }
    }
    
    for round_num in range(1, 4):
        round_data = {
            "round": round_num,
            "agents": {}
        }
        
        for agent_id in ["A", "B", "C"]:
            response = agent_responses[agent_id][round_num - 1]
            round_data["agents"][agent_id] = {
                "reasoning": response['reasoning'],
                "answer": response['answer'],
                "confidence": response.get('confidence', None),
                "tool_used": response.get('tool_used', False)
            }
        
        data["debate_rounds"].append(round_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def create_summary_html(results: List[Dict], output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/summary_{timestamp}.html"
    
    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Debate Experiment Results</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #4CAF50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .correct {
            color: #4CAF50;
            font-weight: bold;
        }
        .incorrect {
            color: #f44336;
            font-weight: bold;
        }
        .condition-tag {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .condition-Baseline { background-color: #9E9E9E; }
        .condition-Fake_Tool { background-color: #FF9800; }
        .condition-Implicit { background-color: #2196F3; }
        .condition-Explicit { background-color: #4CAF50; }
        .condition-Explicit_Autonomous { background-color: #9C27B0; }
        .persuaded-yes {
            background-color: #ffebee;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>🤖 Multi-Agent Debate Experiment Results</h1>
"""
    
    total_debates = len(results)
    total_persuaded = sum(1 for r in results if r['is_persuaded'])
    avg_tool_usage = sum(r['tool_used_count'] for r in results) / total_debates if total_debates > 0 else 0
    avg_challenges = sum(r['challenge_count'] for r in results) / total_debates if total_debates > 0 else 0
    
    conditions_count = {}
    for r in results:
        cond = r['condition']
        if cond not in conditions_count:
            conditions_count[cond] = {'total': 0, 'persuaded': 0}
        conditions_count[cond]['total'] += 1
        if r['is_persuaded']:
            conditions_count[cond]['persuaded'] += 1
    
    html += f"""
    <div class="summary-stats">
        <div class="stat-card">
            <h3>전체 토론 수</h3>
            <div class="value">{total_debates}</div>
        </div>
        <div class="stat-card">
            <h3>설득 성공</h3>
            <div class="value">{total_persuaded}</div>
        </div>
        <div class="stat-card">
            <h3>설득률</h3>
            <div class="value">{(total_persuaded/total_debates*100) if total_debates > 0 else 0:.1f}%</div>
        </div>
        <div class="stat-card">
            <h3>평균 도구 사용</h3>
            <div class="value">{avg_tool_usage:.2f}</div>
        </div>
        <div class="stat-card">
            <h3>평균 반박 횟수</h3>
            <div class="value">{avg_challenges:.2f}</div>
        </div>
    </div>
    
    <h2>조건별 설득률</h2>
    <table>
        <thead>
            <tr>
                <th>조건</th>
                <th>전체 토론</th>
                <th>설득 성공</th>
                <th>설득률</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for cond, stats in sorted(conditions_count.items()):
        persuasion_rate = (stats['persuaded'] / stats['total'] * 100) if stats['total'] > 0 else 0
        html += f"""
            <tr>
                <td><span class="condition-tag condition-{cond}">{cond}</span></td>
                <td>{stats['total']}</td>
                <td>{stats['persuaded']}</td>
                <td><strong>{persuasion_rate:.1f}%</strong></td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <h2>전체 토론 결과</h2>
    <table>
        <thead>
            <tr>
                <th>Question ID</th>
                <th>조건</th>
                <th>Agent A</th>
                <th>Agent B</th>
                <th>Agent C</th>
                <th>A 정답</th>
                <th>설득 여부</th>
                <th>도구 사용</th>
                <th>반박</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for r in results:
        persuaded_class = "persuaded-yes" if r['is_persuaded'] else ""
        a_correct = '<span class="correct">✅</span>' if r['a_is_correct'] else '<span class="incorrect">❌</span>'
        persuaded = '<span class="correct">✅</span>' if r['is_persuaded'] else '<span class="incorrect">❌</span>'
        
        html += f"""
            <tr class="{persuaded_class}">
                <td>{r['question_id']}</td>
                <td><span class="condition-tag condition-{r['condition']}">{r['condition']}</span></td>
                <td>{r['agent_a_final_answer']}</td>
                <td>{r['agent_b_final_answer']}</td>
                <td>{r['agent_c_final_answer']}</td>
                <td>{a_correct}</td>
                <td>{persuaded}</td>
                <td>{r['tool_used_count']}</td>
                <td>{r['challenge_count']}</td>
            </tr>
"""
    
    html += f"""
        </tbody>
    </table>
    
    <div class="footer">
        <p>생성 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p>Multi-Agent Debate Experiment - Tool Attribution & Autonomy Study</p>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

def create_markdown_summary(results: List[Dict], output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/summary_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Multi-Agent Debate Experiment Results\n\n")
        f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total_debates = len(results)
        total_persuaded = sum(1 for r in results if r['is_persuaded'])
        
        f.write("## 전체 요약\n\n")
        f.write(f"- **전체 토론 수**: {total_debates}\n")
        f.write(f"- **설득 성공**: {total_persuaded}\n")
        f.write(f"- **설득률**: {(total_persuaded/total_debates*100) if total_debates > 0 else 0:.1f}%\n\n")
        
        f.write("## 조건별 설득률\n\n")
        f.write("| 조건 | 전체 토론 | 설득 성공 | 설득률 |\n")
        f.write("|------|----------|----------|--------|\n")
        
        conditions_count = {}
        for r in results:
            cond = r['condition']
            if cond not in conditions_count:
                conditions_count[cond] = {'total': 0, 'persuaded': 0}
            conditions_count[cond]['total'] += 1
            if r['is_persuaded']:
                conditions_count[cond]['persuaded'] += 1
        
        for cond, stats in sorted(conditions_count.items()):
            persuasion_rate = (stats['persuaded'] / stats['total'] * 100) if stats['total'] > 0 else 0
            f.write(f"| {cond} | {stats['total']} | {stats['persuaded']} | {persuasion_rate:.1f}% |\n")
        
        f.write("\n## 전체 토론 결과\n\n")
        f.write("| Q ID | 조건 | Agent A | Agent B | Agent C | A 정답 | 설득 | 도구 | 반박 |\n")
        f.write("|------|------|---------|---------|---------|--------|------|------|------|\n")
        
        for r in results:
            a_correct = "✅" if r['a_is_correct'] else "❌"
            persuaded = "✅" if r['is_persuaded'] else "❌"
            f.write(f"| {r['question_id']} | {r['condition']} | {r['agent_a_final_answer']} | ")
            f.write(f"{r['agent_b_final_answer']} | {r['agent_c_final_answer']} | ")
            f.write(f"{a_correct} | {persuaded} | {r['tool_used_count']} | {r['challenge_count']} |\n")
    
    return filename
