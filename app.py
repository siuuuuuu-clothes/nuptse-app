import streamlit as st
import requests
import pandas as pd
import urllib.parse # URLを作るための道具

# ページ設定
st.set_page_config(page_title="Brand Digger Pro", layout="wide")

# ==========================================
# 👇 ユーザー設定エリア
# ==========================================
APP_ID = '1026858885431637322'
AFFILIATE_ID = '5024e14a.9af79762.5024e14b.33fb1c76'

# 📚 ブランド辞書
brand_db = {
    "A": {
        "Acne Studios (Jeans)": ["Acne Studios デニム", 15000, 40000],
        "Arc'teryx (Beta)": ["アークテリクス Beta", 40000, 70000],
    },
    "N": {
        "Nike (Air Force 1)": ["Nike Air Force 1", 10000, 20000],
        "North Face (Nuptse)": ["ノースフェイス ヌプシジャケット", 30000, 50000],
        "North Face (Baltro)": ["ノースフェイス バルトロライトジャケット", 50000, 85000],
    },
    "S": {
        "Supreme (Tee)": ["Supreme Tシャツ", 8000, 20000],
    },
}

# ==========================================
# 🎨 サイドバー
# ==========================================
st.sidebar.title("🔍 Brand Digger Pro")

valid_chars = sorted([k for k, v in brand_db.items() if v])
selected_char = st.sidebar.selectbox("頭文字", valid_chars)
brand_list = brand_db[selected_char]
selected_item_name = st.sidebar.radio(f"{selected_char}のアイテム", list(brand_list.keys()))

item_data = brand_list[selected_item_name]
search_keyword = item_data[0]
default_min = item_data[1]
default_max = item_data[2]

st.sidebar.divider()
st.sidebar.subheader("💰 予算設定")
min_price = st.sidebar.number_input("下限価格", value=default_min, step=1000, key=f"min_{selected_item_name}")
max_price = st.sidebar.number_input("上限価格", value=default_max, step=1000, key=f"max_{selected_item_name}")
st.sidebar.divider()
ng_words = st.sidebar.text_input("除外ワード", value="中古 古着 used ランク キッズ Kids ベスト")

# ==========================================
# 🚀 メイン画面
# ==========================================
st.title(f"Check: {selected_item_name}")
st.caption(f"検索ワード: 「{search_keyword}」")

# 🔥 ここが新機能：他サイトへのリンクボタン生成
# 検索ワードをURL用に変換（エンコード）
encoded_keyword = urllib.parse.quote(search_keyword)

st.write("▼ 他のサイトの相場もチェックする")
col_a, col_y, col_m = st.columns(3)
with col_a:
    st.link_button("Amazonで検索 ➤", f"https://www.amazon.co.jp/s?k={encoded_keyword}")
with col_y:
    st.link_button("Yahoo!で検索 ➤", f"https://shopping.yahoo.co.jp/search?p={encoded_keyword}")
with col_m:
    st.link_button("メルカリで検索 ➤", f"https://jp.mercari.com/search?keyword={encoded_keyword}")

st.divider()

if st.button("楽天の在庫をディグる (検索開始)"):
    
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
        df = df.sort_values('価格').head(30).reset_index(drop=True)
        
        st.success(f"検索完了！ {len(df)}件の楽天在庫が見つかりました。")
        
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
                    st.link_button("楽天で見る ➤", row['URL'])
                st.divider()
    else:
        st.error("楽天には条件に合う在庫がありませんでした。上のボタンからAmazonやメルカリを見てみてください。")
