import streamlit as st
import requests
import pandas as pd

# ページ設定
st.set_page_config(page_title="Brand Digger Pro", layout="wide")

# ==========================================
# 👇 ユーザー設定エリア
# ==========================================
APP_ID = '1026858885431637322'  # あなたのアプリID
AFFILIATE_ID = '5024e14a.9af79762.5024e14b.33fb1c76' # あなたのアフィリエイトID

# 📚 ブランド辞書（Pro版）
# 書き方: "表示名": ["検索キーワード", 下限価格(安い方), 上限価格(高い方)]
brand_db = {
    "A": {
        "Acne Studios (Jeans)": ["Acne Studios デニム", 15000, 40000],
        "Arc'teryx (Beta)": ["アークテリクス Beta", 40000, 70000],
    },
    "N": {
        "Nike (Air Force 1)": ["Nike Air Force 1", 10000, 20000], # 👈 追加！安めの設定
        "Nike (Jordan 1)": ["Air Jordan 1 High", 15000, 35000],
        "North Face (Nuptse)": ["ノースフェイス ヌプシジャケット", 30000, 50000],
        "North Face (Baltro)": ["ノースフェイス バルトロライトジャケット", 50000, 85000], # 👈 追加！高めの設定
    },
    "P": {
        "Patagonia (Retro-X)": ["パタゴニア レトロX", 20000, 40000],
    },
    "S": {
        "Supreme (Tee)": ["Supreme Tシャツ", 8000, 20000],
        "Supreme (Hoodie)": ["Supreme パーカー", 25000, 50000],
    },
}

# ==========================================
# 🎨 サイドバー（検索条件の設定）
# ==========================================
st.sidebar.title("🔍 Brand Digger Pro")

# 1. アルファベット選択
# 中身があるものだけ表示する安全装置
valid_chars = sorted([k for k, v in brand_db.items() if v])
if not valid_chars:
    st.error("辞書が空っぽです！")
    st.stop()

selected_char = st.sidebar.selectbox("頭文字", valid_chars)

# 2. ブランド・アイテム選択
brand_list = brand_db[selected_char]
if not brand_list:
    st.sidebar.warning("アイテムがありません。")
    st.stop()

selected_item_name = st.sidebar.radio(f"{selected_char}のアイテム", list(brand_list.keys()))

# 辞書からデータを取り出す（キーワード、推奨下限、推奨上限）
item_data = brand_list[selected_item_name]
search_keyword = item_data[0]
default_min = item_data[1]
default_max = item_data[2]

st.sidebar.divider()

# 3. 価格設定（自動で切り替わりますが、手動で微調整も可能）
st.sidebar.subheader("💰 予算設定")
# keyを設定することで、アイテムを変えるたびにリセットされるようにする
min_price = st.sidebar.number_input("下限価格 (円)", value=default_min, step=1000, key=f"min_{selected_item_name}")
max_price = st.sidebar.number_input("上限価格 (円)", value=default_max, step=1000, key=f"max_{selected_item_name}")

st.sidebar.divider()

# 4. 除外ワード設定
st.sidebar.subheader("🚫 除外ワード")
ng_words = st.sidebar.text_input("除外する言葉", value="中古 古着 used ランク キッズ Kids ベスト Vest レンタル")

# ==========================================
# 🚀 メイン画面（検索実行）
# ==========================================
st.title(f"Check: {selected_item_name}")
st.caption(f"検索: 「{search_keyword}」 | 予算: {min_price:,}円 〜 {max_price:,}円")

if st.button("市場をディグる (検索開始)"):
    
    base_url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'
    
    progress_text = "楽天の倉庫を捜索中..."
    my_bar = st.progress(0, text=progress_text)

    all_items = []
    max_page = 5
    
    for page in range(1, max_page + 1): 
        my_bar.progress(int((page / max_page) * 100), text=f"{progress_text} ({page}/{max_page}ページ)")
        
        params = {
            'applicationId': APP_ID,
            'affiliateId': AFFILIATE_ID,
            'keyword': search_keyword, 
            'format': 'json',
            'sort': '+itemPrice',
            'availability': 1,
            'minPrice': min_price,
            'maxPrice': max_price,
            'hits': 30,
            'page': page,
            'NGKeyword': ng_words 
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            if 'Items' in data:
                for item in data['Items']:
                    info = item['Item']
                    link_url = info.get('affiliateUrl', info['itemUrl'])

                    all_items.append({
                        '価格': info['itemPrice'],
                        'ショップ': info['shopName'],
                        '商品名': info['itemName'],
                        'URL': link_url,
                        '画像': info.get('mediumImageUrls', [{}])[0].get('imageUrl', '')
                    })
        except:
            pass

    my_bar.empty()

    if all_items:
        df = pd.DataFrame(all_items)
        df = df.drop_duplicates(subset=['URL'])
        # 価格順、トップ30
        df = df.sort_values('価格').head(30).reset_index(drop=True)
        
        st.success(f"検索完了！ {len(df)}件のお宝候補が見つかりました。")
        
        for i, row in df.iterrows():
            price = "{:,}".format(row['価格'])
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{i+1}位：{price}円")
                    st.write(f"**{row['ショップ']}**")
                    st.write(row['商品名'])
                with col2:
                    if row['画像']:
                        st.image(row['画像'], width=100)
                    st.link_button("商品ページへ ➤", row['URL'])
                st.divider()
    else:
        st.error(f"見つかりませんでした。設定価格（{min_price:,}円〜）が安すぎるかもしれません。")
