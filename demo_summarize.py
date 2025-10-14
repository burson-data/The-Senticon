import pandas as pd

# Sample data for testing
data = {
 'URL': [
     'https://www.detik.com/edu/detikpedia/d-5590978/pengertian-artificial-intelligence-ai-fungsi-dan-jenisnya',
     'https://www.kompas.com/tren/read/2023/05/15/063000165/apa-itu-artificial-intelligence--pengertian-cara-kerja-dan-contohnya',
     'https://tekno.kompas.com/read/2023/03/20/16030017/mengenal-chatgpt-dan-dampaknya-bagi-dunia-pendidikan',
     'https://www.cnnindonesia.com/teknologi/20230301143045-185-920345/mengenal-chatgpt-yang-bikin-heboh-dunia',
     'https://www.liputan6.com/tekno/read/5200567/pengertian-machine-learning-jenis-dan-cara-kerjanya'
 ],
 'Judul': [
     'Pengertian Artificial Intelligence (AI), Fungsi dan Jenisnya',
     'Apa Itu Artificial Intelligence? Pengertian, Cara Kerja, dan Contohnya',
     'Mengenal ChatGPT dan Dampaknya bagi Dunia Pendidikan',
     'Mengenal ChatGPT yang Bikin Heboh Dunia',
     'Pengertian Machine Learning, Jenis, dan Cara Kerjanya'
 ],
 'Snippet': [
     'Artificial Intelligence atau AI adalah teknologi yang memungkinkan komputer untuk meniru kecerdasan manusia dalam memproses informasi dan mengambil keputusan.',
     'AI adalah cabang ilmu komputer yang berfokus pada pembuatan sistem yang dapat melakukan tugas-tugas yang biasanya memerlukan kecerdasan manusia.',
     'ChatGPT adalah model bahasa AI yang dikembangkan OpenAI, mampu menghasilkan teks mirip manusia dan menjawab berbagai pertanyaan dengan akurat.',
     'ChatGPT merupakan chatbot AI yang viral karena kemampuannya memberikan respons seperti percakapan manusia pada berbagai topik.',
     'Machine Learning adalah subset dari AI yang memungkinkan komputer belajar dan membuat keputusan tanpa diprogram secara eksplisit.'
 ],
 'Kategori': [
     'Teknologi',
     'Teknologi', 
     'Pendidikan',
     'Teknologi',
     'Teknologi'
 ]
}

df = pd.DataFrame(data)
df.to_excel('demo_news_data.xlsx', index=False)
print("Demo Excel file created: demo_news_data.xlsx")
print("\nKolom yang tersedia:")
for col in df.columns:
 print(f"- {col}")
print("\nFile ini dapat digunakan untuk testing fitur Upload File Excel")
