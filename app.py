import streamlit as st
import dashscope
from dashscope import Generation
import csv
import json
from datetime import datetime

# 1. 网页配置
st.set_page_config(page_title="我的 AI 智能记账本", page_icon="💰")

# --- 这里填入你的秘钥 ---
dashscope.api_key = "sk-b303546b2df74d7d9158d5092a286eb5"

st.title("💰 我的 AI 智能记账本")
st.markdown("---")

# 2. 左侧边栏：显示历史记录
st.sidebar.header("📊 历史记录预览")
try:
    with open('account.csv', 'r', encoding='utf-8-sig') as f:
        # 读取最后5行并显示
        lines = f.readlines()
        for line in lines[-5:]:
            st.sidebar.text(line.strip())
except:
    st.sidebar.write("暂无记录")

# 3. 主界面：输入区
user_text = st.text_input("告诉 AI 你花了什么钱？", placeholder="例如：刚才打车花了25元")

if st.button("开始记账"):
    if user_text:
        with st.spinner('AI 正在分析账单...'):
            # 这里的 Prompt 我们用英文+中文，确保 AI 100% 懂你的意思且不报错
            prompt = f"你是一个记账助手。请从: '{user_text}' 中提取金额、类别、备注。只返回JSON格式，如{{\"amount\": \"15\", \"category\": \"餐饮\", \"note\": \"吃面\"}}"
            
            response = Generation.call(
                model="qwen-turbo",
                prompt=prompt
            )
            
            if response.status_code == 200:
                # 提取 AI 的回复
                result_text = response.output.text
                try:
                    # 将 AI 的 JSON 结果转为 Python 字典
                    data = json.loads(result_text)
                    
                    # 漂亮地显示出来
                    st.success("✅ 识别成功！")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("金额", f"￥{data.get('amount', '0')}")
                    col2.metric("类别", data.get('category', '未知'))
                    col3.metric("备注", data.get('note', '无'))
                    
                    # 保存到文件
                    now = datetime.now().strftime("%Y-%m-%d")
                    with open('account.csv', 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([now, data.get('amount'), data.get('category'), data.get('note')])
                    
                    st.balloons() # 撒花庆祝！
                except:
                    st.error("AI 返回的格式不太对，请再试一次。")
                    st.write("AI 原始回复：", result_text)
            else:
                st.error(f"连接失败：{response.message}")
    else:
        st.warning("你还没说话呢！")
# 2. 在网页底部增加一个“下载/查看完整账单”的功能
st.markdown("---")
if st.checkbox("查看完整历史账单"):
    try:
        import pandas as pd # 如果没安装，终端执行 pip install pandas
        df = pd.read_csv('account.csv', names=['日期', '金额', '类别', '备注'])
        st.dataframe(df) # 在网页上显示精美的表格
    except:
        st.info("账本还是空的，快去记一笔吧！")