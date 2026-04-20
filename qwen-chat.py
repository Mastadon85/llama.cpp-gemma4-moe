import json
import requests
import sys
import time
import subprocess
import re

# Configuration
SERVER_URL = "http://127.0.0.1:11434/v1/chat/completions"

def get_system_stats():
    stats = {"gpu_vram": "N/A", "server_mem": "N/A", "raw_vram": 0}
    try:
        # Get GPU VRAM using nvidia-smi
        gpu_out = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], encoding='utf-8')
        stats["raw_vram"] = int(gpu_out.strip())
        stats["gpu_vram"] = f"{stats['raw_vram']}MB"
        
        # More robust process memory lookup
        mem_out = subprocess.check_output('tasklist /NH /FO CSV', encoding='utf-8')
        for line in mem_out.splitlines():
            if "llama-server" in line.lower():
                # Format is: "Image Name","PID","Session Name","Session#","Mem Usage"
                # Use regex to find the memory part (usually the last quoted field)
                m = re.findall(r'"([^"]*)"', line)
                if len(m) >= 5:
                    mem_str = re.sub(r'[^\d]', '', m[4])
                    if mem_str:
                        mem_mb = int(mem_str) // 1024
                        stats["server_mem"] = f"{mem_mb}MB"
                        break
    except:
        pass
    return stats

def chat():
    print("--- Qwen 3.6 API Link Established ---")
    print(f"Target: {SERVER_URL}")
    print("Mode: API Stream (Zero VRAM/RAM Impact)")
    print("Type 'exit' to quit.\n")

    messages = []

    while True:
        try:
            user_input = input("\033[94mUser: \033[0m")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # File Loading Logic
            if user_input.startswith("/load "):
                file_path = user_input[6:].strip()
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    print(f"\033[93m[System] Loading {len(file_content)} chars from {file_path} (Single-Payload Mode)\033[0m")
                    user_input = f"CONTEXT FROM FILE ({file_path}):\n\n{file_content}"
                except Exception as e:
                    print(f"\033[91m[Error] Could not load file: {e}\033[0m")
                    continue
            
            messages.append({"role": "user", "content": user_input})

            payload = {
                "model": "qwen",
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 4096,
                "return_progress": True,
                "stream_options": {"include_usage": True}
            }

            print("\033[92mAssistant: \033[0m", end="", flush=True)
            
            start_time = time.time()
            response = requests.post(SERVER_URL, json=payload, stream=True)
            full_response = ""
            is_ingesting = True
            stats = {}

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_content = line_str[6:]
                        if data_content == "[DONE]":
                            break
                        
                        chunk = json.loads(data_content)
                        
                        elapsed = time.time() - start_time
                        
                        # Handle Progress
                        if 'prompt_progress' in chunk:
                            p = chunk['prompt_progress']
                            total = p.get('total', 1)
                            processed = p.get('processed', 0)
                            percent = (processed / total) * 100
                            bar_len = 20
                            filled = int(bar_len * processed // total)
                            bar = "█" * filled + "░" * (bar_len - filled)
                            print(f"\r\033[93m[Ingesting: {bar} {percent:3.1f}% | {elapsed:.1f}s]\033[0m", end="", flush=True)
                            continue

                        if 'usage' in chunk:
                            stats['usage'] = chunk['usage']
                        if 'timings' in chunk:
                            stats['timings'] = chunk['timings']

                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            content = delta.get('content')
                            
                            if content:
                                if is_ingesting:
                                    print("\r\033[K\033[92mAssistant: \033[0m", end="", flush=True)
                                    is_ingesting = False
                                print(content, end="", flush=True)
                                full_response += content

            total_elapsed = time.time() - start_time
            print("\n")
            
            # Post-Request Live Stats
            sys_stats = get_system_stats()
            
            # Display Stats
            if stats:
                u = stats.get('usage', {})
                t = stats.get('timings', {})
                prompt_t = u.get('prompt_tokens', 0)
                comp_t = u.get('completion_tokens', 0)
                total_t = prompt_t + comp_t
                
                gen_ms = t.get('predicted_ms') or t.get('t_ms')
                prompt_ms = t.get('prompt_ms')
                
                tps = prompt_t/(prompt_ms/1000) if prompt_ms else 0
                
                # Efficiency Heuristic
                # Qwen 35B f16 is ~17.4MB per 1k tokens. Base is ~16880MB.
                projected_f16 = 16880 + (total_t * 0.0174)
                efficiency = "Baseline"
                if sys_stats['raw_vram'] > 0:
                    vram_diff = projected_f16 - sys_stats['raw_vram']
                    if vram_diff > 500:
                        efficiency = f"SAVED {vram_diff:.0f}MB"
                    elif vram_diff < -500:
                        efficiency = "High Usage"
                    
                    if tps > 0 and tps < 200:
                        efficiency += " (SLOW MODE)"

                stat_line = f"\033[90m[Total: {total_elapsed:.1f}s"
                stat_line += f" | Prompt: {prompt_t} t ({tps:.1f} t/s)"
                stat_line += f" | Gen: {comp_t} t"
                stat_line += f" | GPU: {sys_stats['gpu_vram']} ({efficiency})"
                stat_line += f" | Srv RAM: {sys_stats['server_mem']}"
                stat_line += "]\033[0m"
                print(stat_line)

            messages.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    chat()


if __name__ == "__main__":
    chat()
