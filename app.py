import streamlit as st
import os
import asyncio
import edge_tts
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Museum Alive", page_icon="🏛️")
st.title("🏛️ Museum Alive")
st.caption("输入文物名称，AI 唤醒它的灵魂 ✨")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("⚠️ DEEPSEEK_API_KEY missing!")
        st.stop()
    else:
        st.success("✅ AI Connected")
    
    st.markdown("---")
    st.markdown("**🧠 DeepSeek-V3** · Text Generation")
    st.markdown("**🗣️ Edge-TTS** · Voice Synthesis")

# Initialize DeepSeek Client
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# --- Core Functions ---

async def generate_audio(text, output_file="output.mp3"):
    """Generate audio using Edge-TTS"""
    communicate = edge_tts.Communicate(text, "zh-CN-YunxiNeural")
    await communicate.save(output_file)

def get_artifact_story(artifact_name):
    """Ask DeepSeek to roleplay as this artifact"""
    prompt = f"""
    你是一件名为「{artifact_name}」的文物/历史遗迹，刚刚被唤醒。
    
    请用第一人称（"我"）做一个自我介绍。
    
    要求：
    1. 开头要吸引人，像是沉睡千年刚苏醒。
    2. 讲你的历史、故事和感受，不要只说枯燥的数据。
    3. 语气符合你的身份（古代青铜器要庄重，兵马俑可以幽默）。
    4. 篇幅控制在 150 字以内。
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个博物馆里的文物或历史遗迹，富有性格和情感。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"我好像还没完全醒过来... ({str(e)})"

# --- Main UI ---

artifact_name = st.text_input(
    "🔮 输入文物名称",
    placeholder="例如：三星堆青铜面具、四行仓库、清明上河图..."
)

if artifact_name and st.button("唤醒 🗣️", type="primary", use_container_width=True):
    with st.spinner("正在唤醒沉睡的灵魂..."):
        # Generate Story
        story = get_artifact_story(artifact_name)
        
        # Display
        st.markdown(f"### 📜「{artifact_name}」说：")
        st.info(story)
        
        # Generate & Play Audio
        output_file = "artifact_voice.mp3"
        asyncio.run(generate_audio(story, output_file))
        
        if os.path.exists(output_file):
            st.audio(output_file, autoplay=True)
            st.success("🎉 语音生成成功！")
