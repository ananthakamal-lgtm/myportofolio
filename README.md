### Tugas 1

1. **Penggunaan Elemen Semantik HTML5:**
   Ya, saya secara aktif memanfaatkan elemen-elemen semantik HTML5 seperti `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<figure>`/`<dl>`, dan `<footer>`. 
   Elemen-elemen ini sangat esensial dalam membangun static web karena:
   - **Pemisahan Konteks yang Jelas:** Membantu membedakan unit tematik utama halaman (`<section class="hero">` dan `<section class="projects-section">`) dengan entitas konten mandiri (`<article class="project-card">`). Hal ini mengeliminasi masalah *div soup* dan mempermudah pemeliharaan kode secara modular.
   - **Aksesibilitas (Accessibility/a11y):** Browser dan pembaca layar (*screen reader*) dapat secara otomatis mengenali *implicit ARIA landmarks* (seperti peran navigasi pada `<nav>` dan konten utama pada `<main>`), sehingga mempermudah navigasi bagi pengguna disabilitas tanpa perlu menambahkan atribut ARIA manual secara berlebihan.
   - **Standar SEO & Parsing Struktur:** Membantu mesin pencari mengidentifikasi bagian mana yang merupakan metadata profil, judul hierarki (`h1`-`h3`), serta entitas portofolio mandiri.

2. **Tantangan Tata Letak Responsif dan Evaluasi Elemen:**
   - **Tantangan Utama:** Mengelola layout asimetris pada hero section—khususnya elemen aksen dekoratif `.photo-block` di balik foto profil—serta mengatur kartu proyek agar tidak terhimpit saat ukuran layar menyempit.
   - **Strategi Evaluasi & Rekonfigurasi Tata Letak:**
     - **Hero Layout (Desktop vs Mobile):** Pada desktop, grid diatur 2 kolom dengan rasio `1.3fr 1fr`. Saat beralih ke mobile (< 600px), grid diubah menjadi 1 kolom vertikal dengan urutan visual berprioritas: `identity` (nama & asal instansi) &rarr; `photo` &rarr; `details` (bio, NPM, dan link kontak). Ukuran foto dibatasi (`max-width: 220px`) agar tidak menghabiskan seluruh area layar atas (*above-the-fold*).
     - **Kartu Proyek Adaptif:** Memanfaatkan CSS Grid dengan `repeat(auto-fit, minmax(270px, 1fr))`. Properti ini memungkinkan browser secara otomatis menentukan jumlah kolom terbaik sesuai lebar viewport tanpa horizontal overflow. Pada viewport tablet/mobile (< 768px), layout langsung beralih mulus ke 1 kolom vertikal.
     - **Tipografi Dinamis:** Menggunakan fungsi `clamp()` pada judul utama (`h1`) dan judul section (`h2`) agar skala font menyusut proporsional secara *fluid* mengikuti lebar layar.

3. **Batasan Static Web dan Rencana Fungsionalitas Dinamis:**
   - **Batasan Static Web Saat Ini:** Seluruh data profil dan rincian proyek bersifat *hardcoded* di dalam berkas HTML. Menambah proyek baru atau mengubah riwayat bio mengharuskan modifikasi kode sumber secara langsung yang rawan merusak susunan markup (*syntax error*). Selain itu, tidak ada kemampuan untuk menyaring (*filtering*) proyek berdasarkan kategori atau menerima pesan interaktif melalui form kontak.
   - **Fungsionalitas Dinamis yang Direncanakan (Iterasi Selanjutnya):**
     - **Arsitektur Django MVT (Model-View-Template):** Membuat model database seperti `Project` dan `Profile` pada `models.py`, sehingga data dapat dikelola secara modular dan fleksibel melalui Django Admin interface.
     - **Dynamic Rendering:** Memanfaatkan Django Template Engine (`{% for project in projects %}`) untuk merender kartu proyek secara otomatis dari basis data.
     - **Interaktivitas & Feedback:** Mengimplementasikan form kontak fungsional dengan validasi backend (Django Forms & CSRF token protection) untuk mencatat pesan pengunjung ke basis data.

---

### AI Disclosure

Pengerjaan Tugas 1 ini memanfaatkan generative AI (Gemini) sebagai asisten perancangan dan diskusi teknis dengan rincian sebagai berikut:
- **Tools yang Digunakan:** Gemini.
- **Aspek yang Dibantu:**
  1. Memberikan usulan struktur HTML semantik untuk section *Featured Projects* dan mendiskusikan implementasi CSS Grid yang harmonis dengan gaya desain neo-brutalist / editorial yang sudah saya buat di Tutorial 01.
  2. Menyusun draf awal analisis konseptual untuk 3 pertanyaan reflektif.
- **Keterbatasan AI & Validasi Mandiri yang Dilakukan:**
  - AI awalnya cenderung menyarankan styling modern bertema *dark mode* generik atau menambahkan library CSS eksternal. Saya secara sadar menolak hal tersebut dan menyelaraskan kode CSS murni agar tetap patuh pada variabel warna (`--paper`, `--ink`, `--accent`, `--line`) dan font *Space Grotesk* dari basis kode orisinal saya.
  - Saya melakukan pengujian manual menyeluruh terhadap responsivitas tata letak di Chrome DevTools pada berbagai resolusi (*breakpoint* 375px, 600px, 768px, dan 1024px) untuk memastikan tidak ada *overflow* horizontal dan seluruh efek hover berfungsi baik.