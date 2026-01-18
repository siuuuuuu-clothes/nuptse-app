import streamlit as st
import requests
import pandas as pd

# ページの設定
st.set_page_config(page_title="ヌプシ最安値チェッカー", layout="wide")

# タイトル
st.title("🧥 ノースフェイス ヌプシジャケット 最安値探索くん")
st.write("楽天中の在庫をスキャンして、4万円以下の新品・正規品を安い順に表示します。")

# アプリID（入力済み）
APP_ID = '1026858885431637322'

# アフィリエイトID（入力済み）
AFFILIATE_ID = '5024e14a.9af79762.5024e14b.33fb1c76'

# ボタンを押したら実行
if st.button("最安値を検索する"):
    
    base_url = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601'
    
    # 進行状況バーの表示
    progress_text = "楽天の倉庫を捜索中..."
    my_bar = st.progress(0, text=progress_text)

    all_items = []
    
    # 10ページ分探す
    for page in range(1, 11): 
        # プログレスバーを更新
        my_bar.progress(page * 10, text=f"{progress_text} ({page}0%)")
        
        params = {
            'applicationId': APP_ID,
            'affiliateId': AFFILIATE_ID, # 👈【重要】この1行を必ず追加してください！
            'keyword': 'ノースフェイス ヌプシジャケット', 
            'format': 'json',
            'sort': '+itemPrice',
            'availability': 1,
            'minPrice': 28000,
            'maxPrice': 42000,
            'hits': 30,
            'page': page,
            'NGKeyword': '中古 古着 used ランク キッズ Kids ベスト Vest' 
        }
        
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            if 'Items' in data:
                for item in data['Items']:
                    info = item['Item']
                    name = info['itemName']
                    # 型番判定
                    model = "不明"
                    if 'ND92555' in name: model = '🆕 24-25モデル'
                    elif 'ND92234' in name: model = '⏹ 22-23モデル'
                    
                    if model != "不明":
                        # リンク先（アフィリエイトIDがあればaffiliateUrlを使う）
                        link_url = info.get('affiliateUrl', info['itemUrl'])

                        all_items.append({
                            'モデル': model,
                            '価格': info['itemPrice'],
                            'ショップ': info['shopName'],
                            '商品名': name,
                            'URL': link_url
                        })
        except:
            pass

    # プログレスバーを消す
    my_bar.empty()

    # データ整理と表示
    if all_items:
        df = pd.DataFrame(all_items)
        # URLで重複削除
        df = df.drop_duplicates(subset=['URL'])
        # 価格順、トップ20
        df = df.sort_values('価格').head(20).reset_index(drop=True)
        
        st.success(f"検索完了！ {len(df)}件の激安商品が見つかりました。")
        
        for i, row in df.iterrows():
            price = "{:,}".format(row['価格'])
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"第{i+1}位：{price}円")
                    st.write(f"**{row['ショップ']}** | {row['モデル']}")
                    st.caption(row['商品名'][:50] + "...")
                with col2:
                    st.link_button("商品ページへ ➤", row['URL'])
                st.divider()
    else:
        st.error("条件に合う商品が見つかりませんでした。売り切れの可能性があります。")
