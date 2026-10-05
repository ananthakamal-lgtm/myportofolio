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

---

### Tugas 2

1. **Alur Request-Response Pemrosesan Halaman Portofolio Baru (`/projects/`):**
   - **Permintaan Masuk (HTTP Request):** Ketika pengguna mengakses alamat URL `http://127.0.0.1:8000/projects/` melalui browser atau mengklik tautan navigasi `Projects`, server web Django menerima permintaan HTTP GET tersebut dan memicu siklus *request-response*.
   - **`portofolio/urls.py` (URLconf Tingkat Proyek):** Django memeriksa konfigurasi URL utama proyek (`ROOT_URLCONF`). Jalur URL dicocokkan dengan entri `urlpatterns`. Saat mencocokkan pattern kosong `""`, fungsi `include("main.urls")` mendelegasikan pemrosesan segmen URL berikutnya ke URLconf aplikasi `main`.
   - **`main/urls.py` (URLconf Tingkat Aplikasi):** URLconf aplikasi membaca sisa path `projects/`. Django menemukan rute `path("projects/", show_projects, name="show_projects")` yang cocok, lalu memanggil fungsi view handler yang bersangkutan, yaitu `show_projects`, dengan menyertakan objek `HttpRequest`.
   - **`main/views.py` (View / Controller):** Fungsi `show_projects(request)` bertindak sebagai koordinator logika bisnis. View berinteraksi dengan layer data melalui Django ORM dengan memanggil `Project.objects.all()`. Seluruh objek proyek diambil dari basis data dan dikemas ke dalam dictionary context bersama variabel pendukung:
     ```python
     context = {
         "name": "Anantha",
         "project_list": Project.objects.all(),
     }
     ```
     View kemudian memanggil fungsi `render(request, "projects.html", context)`.
   - **`main/models.py` (Model):** Merepresentasikan skema tabel data `Project` di database (tabel `main_project` di SQLite). Melalui abstraksi ORM, Django menerjemahkan pemanggilan `Project.objects.all()` menjadi query SQL:
     ```sql
     SELECT id, title, category, description, year, tech_stack, demo_url, repo_url, created_at FROM main_project;
     ```
     dan mengembalikan kumpulan objek model Python ke View.
   - **`templates/projects.html` (Template):** Django Template Engine memproses berkas template HTML. DTL mengevaluasi variabel context dan menjalankan perulangan `{% for project in project_list %}` untuk merender kartu proyek beserta tag teknologi dan tautan live demo / repositori. Apabila data proyek kosong, DTL otomatis mengeksekusi blok kondisional `{% empty %}` untuk menampilkan pesan status kosong (*empty state*).
   - **Respon Dikirimkan ke Browser (HTTP Response):** Hasil kompilasi template menghasilkan teks markup HTML statis yang dibungkus dalam objek `HttpResponse` dengan kode status HTTP `200 OK`, kemudian dikirimkan kembali ke peramban pengguna untuk dirender secara visual.

2. **Alasan Data Disimpan pada Model vs Hard-Coded di Template serta Dampaknya terhadap Pemeliharaan dan Pengembangan:**
   - **Separation of Concerns (Pemisahan Tanggung Jawab):** Template bertugas murni untuk tata letak dan representasi visual (*presentation layer*), sedangkan Model bertanggung jawab atas struktur, integritas, dan persistensi data (*data layer*). Mencampurkan data portofolio langsung ke dalam markup HTML melanggar prinsip arsitektur modular yang bersih.
   - **Kemudahan Pemeliharaan (Maintainability):** Ketika data disimpan di model/basis data, penambahan proyek baru atau koreksi deskripsi dapat dilakukan kapan saja melalui antarmuka Django Admin (`/admin/`) atau database client tanpa menyentuh satu baris pun kode HTML. Sebaliknya, pada data yang di-*hardcode*, modifikasi konten mengharuskan perubahan langsung pada berkas HTML yang meningkatkan risiko *human error* seperti merusak tag penutup, menghilangkan kelas CSS, atau memicu konflik git (*merge conflicts*).
   - **Single Source of Truth & Portabilitas Data:** Data yang tersimpan di model menjadi satu-satunya sumber rujukan terpusat (*single source of truth*). Data tersebut dapat dengan mudah disajikan dalam format lain di masa depan—misalnya endpoint REST API berbasis JSON untuk aplikasi mobile, fitur pencarian/penyaringan berdasarkan kategori/teknologi (*query filtering*), atau pagination—tanpa perlu menduplikasi markup template.
   - **Validasi dan Konsistensi Data:** Model Django memberlakukan batasan dan validasi skema yang ketat (misalnya format tautan pada `URLField`, tipe angka pada `IntegerField`, serta batasan panjang pada `CharField`). Hal ini menjamin bahwa seluruh rekaman data yang tersimpan selalu valid dan konsisten.

3. **Perbedaan Fungsi `makemigrations` dan `migrate` pada Django serta Contoh Skenarionya:**
   - **`python manage.py makemigrations`:**
     - Bertanggung jawab untuk mendeteksi perubahan deklaratif yang dibuat pengembang pada berkas `models.py` (seperti membuat model baru, menambah field, mengubah opsi field, atau menghapus model).
     - Perintah ini **tidak** mengubah atau memodifikasi tabel pada database fisik. Fungsinya adalah menyusun dan menyimpan berkas instruksi Python baru di dalam direktori `migrations/` (misalnya `0002_project.py`) sebagai *blueprint* riwayat evolusi skema.
   - **`python manage.py migrate`:**
     - Bertanggung jawab untuk mengeksekusi berkas-berkas migrasi yang belum diterapkan ke basis data fisik yang sedang dikonfigurasi (misalnya SQLite atau PostgreSQL).
     - Perintah ini menerjemahkan instruksi migrasi Python menjadi sintaks SQL DDL (*Data Definition Language*, seperti `CREATE TABLE` atau `ALTER TABLE`), memperbarui tabel `django_migrations` sebagai penanda versi migrasi yang telah diterapkan, dan menyesuaikan struktur tabel database secara nyata.
   - **Contoh Skenario Perubahan Model:**
     - **Skenario Penambahan Model Baru (Tugas 2):** Ketika membuat class `Project` di `models.py`, kita menjalankan `python manage.py makemigrations` untuk membuat berkas `0002_project.py` yang memuat perintah `migrations.CreateModel(name="Project", ...)`. Setelah itu, kita wajib menjalankan `python manage.py migrate` agar tabel `main_project` terbentuk di `db.sqlite3`. Tanpa `migrate`, aplikasi akan mengalami error `OperationalError: no such table: main_project` saat query dijalankan.
     - **Skenario Penambahan Kolom Baru:** Apabila kelak kita ingin menambahkan field baru pada model `Project`, misalnya `featured = models.BooleanField(default=False)`, kita wajib menjalankan `makemigrations` untuk mencatat penambahan field tersebut ke berkas migrasi baru, lalu menjalankan `migrate` agar Django mengeksekusi `ALTER TABLE main_project ADD COLUMN featured bool DEFAULT 0;` pada database.

---

### AI Disclosure (Tugas 2)

Pengerjaan Individual Assignment 2 ini memanfaatkan generative AI sebagai asisten pemrograman berpasangan (*pair programming*) dan validasi arsitektur perangkat lunak dengan rincian transparansi sebagai berikut:
- **Tools yang Digunakan:** Gemini (Antigravity Assistant).
- **Strategi Prompting:**
  1. Menggunakan prompt bertahap dan terarah (*step-by-step modular prompting*) yang diselaraskan dengan tahapan pola arsitektur MVT (Model &rarr; Migration &rarr; View & URL &rarr; Template & UI &rarr; Unit Testing &rarr; Refleksi).
  2. Memberikan spesifikasi model yang merefleksikan data nyata portofolio dari Tugas 1 agar kontinuitas proyek tetap terjaga dan tidak menggunakan *dummy data* generik.
  3. Meminta panduan strategi pengelolaan Git agar riwayat commit bersifat atomik (*atomic commits*) dan mematuhi konvensi *Conventional Commits* untuk mencapai standar penilaian maksimal.
- **Aspek Spesifik yang Dibantu:**
  1. Membantu merancang struktur class model `Project` pada `main/models.py` dengan 8 field (melampaui syarat minimal 3 field) serta properti helper `tech_list`.
  2. Menghasilkan draf awal berkas template `templates/projects.html` yang selaras dengan styling visual Neo-Brutalist / Editorial dari tugas sebelumnya.
  3. Menyusun skenario pengujian komprehensif pada `main/tests.py` mencakup verifikasi model, routing URL, status code HTTP 200, eksistensi template, rendering data dinamis, dan penanganan kondisi data kosong (*empty state*).
  4. Berdiskusi dan menyusun draf analitis jawaban untuk ketiga pertanyaan reflektif.
- **Keterbatasan AI & Validasi Mandiri oleh Mahasiswa:**
  1. **Validasi Skema & Konsistensi Identitas:** Saya memeriksa dan memastikan setiap commit dijalankan dengan identitas lokal saya (`nantha kml <anantha.kamal@ui.ac.id>`) dan di-*push* secara mandiri ke repositori pribadi.
  2. **Refaktor Kode HTML:** AI awalnya menyarankan mempertahankan kartu statis lama di `index.html`. Saya secara proaktif merefaktor `index.html` agar tidak ada lagi data proyek yang di-*hardcode*, melainkan dialihkan secara elegan menggunakan tautan CTA menuju rute dinamis `/projects/`.
  3. **Verifikasi Test Suite:** Menjalankan `python manage.py test` di environment virtual lokal dan memverifikasi seluruh 10 test case lulus dengan status `OK` tanpa galat.

---

### Tugas 3

1. **Alasan Penggunaan ModelForm pada Django Dibandingkan Membuat Form HTML Manual & Urgensi `{% csrf_token %}`:**
   - **Keunggulan dan Alasan Menggunakan ModelForm:**
     - **Prinsip DRY (*Don't Repeat Yourself*) & Integritas Skema:** Ketika kita telah mendefinisikan skema data pada `models.py` (seperti panjang maksimum `max_length`, tipe data `CharField`, `TextField`, `URLField`, dan pilihan opsi `choices`), membuat form HTML secara manual mengharuskan kita menduplikasi aturan-aturan tersebut di berkas template. Dengan `ModelForm`, Django secara otomatis memetakan setiap field model menjadi elemen input form yang sesuai lengkap dengan tipe data dan batasannya.
     - **Validasi Otomatis dan Sanitasi Data (*Form Cleaning*):** Memvalidasi form HTML manual di backend mengharuskan penulisan logika pengecekan satu per satu pada `request.POST`. Sebaliknya, `ModelForm` menyediakan metode bawaan `form.is_valid()` yang otomatis memvalidasi apakah tipe data sesuai, field wajib telah diisi, dan URL valid. Jika terdapat galat, pesan kesalahan dikumpulkan secara terstruktur dalam `form.errors` dan data yang telah bersih (*sanitized*) tersedia aman di `form.cleaned_data`.
     - **Kemudahan Persistensi Data (Direct ORM Saving):** Pada form manual, pengembang harus mengekstrak setiap nilai dari `request.POST` lalu membuat atau memperbarui objek ORM secara manual (`obj.title = request.POST['title']`, dst.). Dengan `ModelForm`, pemanggilan `form.save()` langsung mengeksekusi operasi `INSERT` atau `UPDATE` ke basis data secara atomik.
     - **Dukungan Alami untuk Operasi Edit/Update (*Instance Binding*):** `ModelForm` dapat menerima parameter `instance=obj`. Seluruh elemen input pada form akan secara otomatis terisi (*pre-populated*) dengan nilai data objek yang sedang diedit tanpa perlu menuliskan atribut `value="{{ ... }}"` manual di markup HTML.
     - **Aksesibilitas dan Keamanan Standar:** `ModelForm` menghasilkan atribut HTML yang terstandarisasi (`id`, `name`, `for` pada tag `<label>`), yang mempermudah navigasi pembaca layar (*screen reader*) serta mengurangi risiko celah keamanan akibat kelalaian penulisan markup manual.
   - **Urgensi Menambahkan `{% csrf_token %}` pada Form:**
     - **Mitigasi Serangan CSRF (*Cross-Site Request Forgery*):** CSRF adalah serangan di mana situs berbahaya pihak ketiga memanfaatkan status autentikasi aktif peramban pengguna (seperti sesi login atau cookie) untuk mengirimkan permintaan HTTP berbahaya tanpa disadari (misalnya melakukan perubahan data atau penghapusan data portofolio).
     - **Mekanisme Perlindungan Django:** Tag `{% csrf_token %}` menghasilkan elemen input tersembunyi (*hidden input field*) yang berisi token kriptografis acak dan unik yang terikat pada sesi pengguna saat ini.
     - **Verifikasi Middleware (`CsrfViewMiddleware`):** Ketika form dikirimkan melalui metode POST, middleware proteksi CSRF Django memverifikasi kecocokan antara token yang dikirimkan dengan token sesi. Apabila token tidak cocok, kedaluwarsa, atau tidak disertakan, Django secara otomatis menolak permintaan dan mengembalikan kode status HTTP `403 Forbidden`. Hal ini menjamin bahwa seluruh mutasi data hanya berasal dari form sah yang dirender oleh aplikasi kita sendiri.

2. **Alasan JSON Lebih Disukai Dibandingkan XML dalam Pengembangan Web Modern:**
   - **Sintaksis Ringkas dan Hemat Bandwidth (*Lightweight & Compact*):** XML memiliki *overhead* karakter yang besar karena mengharuskan setiap data dibungkus oleh tag pembuka dan penutup yang redundan (misalnya `<project><title>Nama Proyek</title></project>`), sedangkan JSON menggunakan notasi pasangan kunci-nilai (*key-value*) yang padat (`{"title": "Nama Proyek"}`). Karakter yang lebih sedikit menghasilkan ukuran berkas yang jauh lebih kecil, mempercepat transmisi data melalui jaringan, dan menghemat konsumsi bandwidth, khususnya pada perangkat seluler.
   - **Parsing Alami (*Native Parsing*) di Lingkungan JavaScript:** JSON (*JavaScript Object Notation*) merupakan bagian intrinsik dari bahasa pemrograman JavaScript yang mendominasi sisi peramban web. Browser modern dapat mem-parsing teks JSON menjadi objek JavaScript secara instan menggunakan metode bawaan `JSON.parse()` yang dieksekusi langsung pada level mesin runtime (misalnya V8) dengan performa sangat tinggi. Sebaliknya, XML memerlukan *parser* dokumen DOM terpisah (`DOMParser` atau query XPath) yang jauh lebih kompleks, memakan memori, dan lambat.
   - **Dukungan Tipe Data Primitif:** JSON secara eksplisit mendukung dan membedakan tipe data bawaan seperti string, number, boolean, array, dan object (null). Di sisi lain, seluruh data di dalam elemen XML secara inheren diperlakukan sebagai teks (*string*), sehingga aplikasi klien harus melakukan konversi tipe data (*type casting*) secara manual.
   - **Standar *De Facto* Arsitektur RESTful API & Frontend Framework:** Seluruh ekosistem web modern—mulai dari framework frontend (React, Vue, Next.js), arsitektur microservices, hingga library HTTP—dibangun dengan pendekatan *first-class citizen* terhadap JSON. Kemudahan pembacaan oleh manusia (*human-readable*) sekaligus kemudahan manipulasi di sisi backend (seperti modul `json` atau `django.core.serializers` pada Python) menjadikan JSON pilihan paling efisien dan ergonomis.

3. **Alur View Mengembalikan Data Portofolio dalam Bentuk JSON & Alasan Perlunya Proses Serialisasi Model:**
   - **Alur yang Terjadi pada Fungsi View:**
     1. **Penerimaan Permintaan HTTP:** Klien (browser atau API consumer) mengirimkan permintaan HTTP GET ke endpoint rute, misalnya `/api/experience/` atau `/api/projects/`.
     2. **Pengambilan Data melalui ORM:** Fungsi view mengeksekusi query database menggunakan Django ORM, misalnya `experiences = Experience.objects.all()`. Database mengembalikan data mentah yang oleh ORM dikonstruksi menjadi kumpulan objek Python dalam memori berupa `QuerySet`.
     3. **Proses Serialisasi (*Serialization*):** Fungsi view memanggil modul serializer bawaan Django: `experiences_json = serializers.serialize("json", experiences)`. Serializer mengiterasi setiap objek model, mengekstrak informasi model, primary key (`pk`), serta kamus atribut `fields`, lalu mengonversinya menjadi string berformat JSON yang valid.
     4. **Pengemasan dan Pengiriman Respons:** String JSON dibungkus ke dalam objek `HttpResponse(experiences_json, content_type="application/json")` dengan kode status HTTP `200 OK`. Header `Content-Type` memberi tahu klien bahwa payload yang dikirimkan adalah dokumen JSON yang siap di-parse.
   - **Alasan Perlunya Proses Serialisasi pada Model Django:**
     - **Inkompatibilitas Format Objek In-Memory Python dengan Protokol HTTP:** Objek model Django (`Experience` atau `Project`) adalah objek kelas Python yang kaya (*complex Python objects*). Objek tersebut memiliki referensi memori internal, metode-metode bisnis, status koneksi database, dan metadata model. Protokol HTTP hanya mampu mentransmisikan data dalam format teks terstruktur berbasis string atau aliran biner (*byte stream*). Kita tidak bisa mengirimkan objek Python mentah melalui kabel jaringan.
     - **Interoperabilitas dan Agnostisisme Platform:** Data portofolio perlu diakses oleh berbagai klien yang mungkin tidak ditulis dalam Python (misalnya JavaScript di browser, Swift di iOS, atau Kotlin di Android). Serialisasi mengubah struktur data internal menjadi format standar terbuka (JSON) yang dapat dipahami dan didekodekan oleh bahasa pemrograman apa pun secara universal.
     - **Format Khusus dan Keamanan Data:** Serialisasi menangani konversi tipe data yang tidak ada secara langsung di JSON murni (seperti `UUID` dan objek waktu `datetime`) menjadi representasi string terstandarisasi (seperti format tanggal ISO 8601). Selain itu, serialisasi memungkinkan kita mengontrol dengan tepat field mana saja yang boleh diekspos ke publik dan menyembunyikan data internal yang sensitif.

---

### AI Disclosure (Tugas 3)

Pengerjaan Individual Assignment 3 ini memanfaatkan generative AI sebagai asisten pemrograman berpasangan (*pair programming*) dan validasi arsitektur perangkat lunak dengan rincian transparansi sebagai berikut:
- **Tools yang Digunakan:** Gemini (Antigravity Assistant).
- **Strategi Prompting:**
  1. **Pendekatan Modular & Berbasis Rencana (*Planning-First Approach*):** Menyusun rencana implementasi komprehensif (`implementation_plan.md`) terlebih dahulu sebelum menulis kode untuk memetakan kebutuhan ModelForm, operasi CRUD, endpoint JSON, serta refactoring template.
  2. **Konsistensi Desain & Kontinuitas Tugas:** Meminta asisten mempertahankan estetika Neo-Brutalist / Editorial dari Tugas 1 dan 2, menggunakan variabel CSS yang ada (`--paper`, `--ink`, `--accent`, `--line`), serta memastikan seluruh form dan modal terintegrasi secara mulus.
  3. **Pengujian Menyeluruh Berbasis TDD/Automation:** Meminta penyusunan unit test komprehensif pada `main/tests.py` untuk memverifikasi setiap endpoint view (GET, POST valid, POST invalid, 404 pada invalid UUID) dan data delivery JSON.
- **Aspek Spesifik yang Dibantu:**
  1. **Perancangan ModelForm:** Merancang `ExperienceForm` pada `main/forms.py` dengan 4 field non-id dan non-timestamp (`title`, `category`, `description`, `thumbnail`), serta menyesuaikan widget dan label berbahasa Indonesia.
  2. **Implementasi CRUD & Deserialisasi JSON:** Membangun fungsi view `create_experience`, `update_experience`, `delete_experience`, `get_experience_json`, serta pola deserialisasi pada `show_experience`. Sebagai nilai tambah, ditambahkan pula fitur `update_project` untuk entitas Proyek.
  3. **Antarmuka & Komponen Popover Modal:** Membuat komponen popover konfirmasi hapus `experience_delete_modal.html` dan template form terpadu `experience_form.html` yang meng-extend `base.html`.
  4. **Penyusunan Test Suite:** Menulis skenario pengujian otomatis komprehensif sehingga total unit tests meningkat menjadi 38 test case yang seluruhnya berstatus lulus (`OK`).
  5. **Sintesis Pertanyaan Reflektif:** Berdiskusi dan menyusun jawaban mendalam serta terstruktur untuk ketiga pertanyaan reflektif Tugas 3.
- **Keterbatasan AI & Validasi Mandiri oleh Mahasiswa:**
  1. **Pengecekan Persyaratan Khusus Tugas:** Mahasiswa memeriksa dan memastikan secara manual bahwa field timestamp (`started_at`, `ended_at`) dan `id` benar-benar dikecualikan dari `ExperienceForm` sesuai ketentuan instruksi tugas.
  2. **Pembersihan Struktur Template:** Mahasiswa memvalidasi bahwa tidak ada duplikasi tag navigasi atau markup ganda pada saat meng-extend `base.html`.
  3. **Verifikasi Manual dan Kontrol Git:** Mahasiswa menguji fungsionalitas form secara langsung pada antarmuka browser di `http://127.0.0.1:8000/` dan mengontrol penuh proses git agar kode direview terlebih dahulu sebelum dilakukan commit dan push.
---

### Tugas 4: Implementasi Autentikasi, Manajemen Hak Akses (Otorisasi 4 Peran), dan Fitur Interaktif Pemberian Star

Pada Individual Assignment 4 ini, sistem autentikasi dan otorisasi dari Tutorial 04 diperluas ke entitas portofolio `Experience` (dari Tugas 3) serta menyelaraskan entitas `Project`, dengan penambahan peran baru **Editor** dan fitur interaktif pemberian **Star**.

#### 1. Arsitektur Matriks Hak Akses (4 Peran)
Sistem menerapkan pembatasan hak akses di sisi server (*server-side authorization*) yang ketat dengan matriks peran sebagai berikut:

| Peran | Membaca (List & Detail) | Memberi / Membatalkan Star | Mengubah Data (Edit/Update) | Membuat Data (Tambah/Create) | Menghapus Data (Delete) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pengunjung Tanpa Login (*Guest*)** | ✅ Ya | ❌ Dialihkan ke `/login/` | ❌ Dialihkan ke `/login/` | ❌ Dialihkan ke `/login/` | ❌ Dialihkan ke `/login/` |
| **Pengguna Biasa (*Authenticated*)** | ✅ Ya | ✅ Ya (`toggle_star`) | ❌ HTTP 403 Forbidden | ❌ HTTP 403 Forbidden | ❌ HTTP 403 Forbidden |
| **Editor (Group `Editor`)** | ✅ Ya | ✅ Ya (`toggle_star`) | ✅ Ya (Form Edit) | ❌ HTTP 403 Forbidden | ❌ HTTP 403 Forbidden |
| **Pemilik Portofolio (*Superuser*)** | ✅ Ya | ✅ Ya (`toggle_star`) | ✅ Ya (Form Edit) | ✅ Ya (Form Tambah) | ✅ Ya (Hapus & Modal) |

#### 2. Implementasi Peran Editor & Otorisasi Sisi Server
- **Penerapan Django Group `Editor` & Permission:**
  - Dibuatkan migrasi data Django (`0007_create_editor_group.py`) yang secara otomatis membuat grup `Editor` di basis data serta mengasosiasikannya dengan permission `main.change_experience` dan `main.change_project`.
  - Akun dapat ditambahkan ke grup `Editor` secara fleksibel melalui antarmuka Django Admin (`/admin`).
- **Pemeriksaan Sisi Server (*Server-Side Checks*):**
  - Menggunakan dekorator `@login_required(login_url="/login/")` pada seluruh endpoint aksi (`create`, `update`, `delete`, `toggle_star`), sehingga pengunjung anonim otomatis dialihkan ke halaman login.
  - Untuk aksi `create` dan `delete`, view memverifikasi `if not request.user.is_superuser: raise PermissionDenied` (mengembalikan respons HTTP 403 Forbidden).
  - Untuk aksi `update`, view memverifikasi `if not (request.user.is_superuser or request.user.groups.filter(name__iexact="Editor").exists() or request.user.has_perm("main.change_experience")): raise PermissionDenied`.
  - Untuk aksi `toggle_star`, setiap pengguna terotentikasi dapat memberikan atau membatalkan star secara aman melalui request HTTP POST berpelindung `{% csrf_token %}`.

#### 3. Penyembunyian Kontrol Aksi pada Template (*Template Control Hiding*)
- **Context Processor `main.context_processors.user_roles`:**
  - Menginjeksikan variabel boolean `is_editor` ke dalam seluruh template Django secara global.
- **Kondisional UI:**
  - Tombol **"+ Tambah Pengalaman"** dan **"+ Tambah Proyek"** dibungkus oleh `{% if user.is_superuser %}`.
  - Tombol **"Edit"** dibungkus oleh `{% if user.is_superuser or is_editor %}`.
  - Tombol **"Hapus"** beserta modal konfirmasi popover dibungkus oleh `{% if user.is_superuser %}`.
  - Tombol **"Star / Unstar"** (`experience_star.html` dan `project_star.html`) menampilkan status personal pengguna (apakah sudah membintangi atau belum) dan total hitungan bintang.

#### 4. Relasi ManyToMany Pemberian Star
- Menambahkan relasi `starred_by = models.ManyToManyField(User, related_name="starred_experiences", blank=True)` pada model `Experience`.
- Mengimplementasikan endpoint view `toggle_experience_star` yang memvalidasi bahwa setiap pengguna terdaftar hanya dapat memberikan maksimal satu star (toggle on/off).

#### 5. Keamanan & Integritas API JSON
- Endpoint `get_experience_json` dan `get_projects_json` tetap berfungsi optimal untuk publikasi data tanpa membocorkan atribut sensitif (seperti password hash, session key, atau email pribadi).

---

### AI Disclosure (Tugas 4)

Pengerjaan Individual Assignment 4 ini memanfaatkan generative AI sebagai asisten pemrograman berpasangan (*pair programming*) dan arsitektur perangkat lunak dengan rincian transparansi sebagai berikut:
- **Tools yang Digunakan:** Gemini (Antigravity Assistant).
- **Strategi Prompting:**
  1. **Spesifikasi Berbasis Matriks Peran (*Role-Matrix First*):** Memetakan matriks 4 peran pengguna (Guest, Regular, Editor, Superuser) secara komprehensif sebelum mengimplementasikan pemeriksaan di view dan template.
  2. **Pengujian Menyeluruh Berbasis TDD (*Test-Driven Automation*):** Mengembangkan test suite pengujian hak akses dan fungsionalitas star pada `main/tests.py` hingga mencakup 62 test case lengkap yang seluruhnya lulus (`OK`).
  3. **Keamanan Berlapis (*Defense in Depth*):** Memastikan pembatasan hak akses tidak hanya terjadi di level antarmuka visual (menyembunyikan tombol), melainkan divalidasi secara absolut di sisi server menggunakan `PermissionDenied` dan `login_required`.
- **Aspek Spesifik yang Dibantu:**
  1. **Perancangan Model & Migrasi:** Menambahkan relasi `starred_by` ManyToManyField pada model `Experience` dan membuat skrip migrasi database `0006_experience_starred_by.py` serta data migration `0007_create_editor_group.py`.
  2. **Implementasi Otorisasi & View Star:** Menuliskan logika otorisasi server-side pada `create_experience`, `update_experience`, `delete_experience`, `update_project`, serta fungsi `toggle_experience_star`.
  3. **Komponen Template & Context Processor:** Merancang `main/context_processors.py` untuk mendistribusikan status `is_editor`, membuat komponen `experience_star.html`, serta memperbarui modal aksi dan template halaman `experience.html` dan `projects.html`.
  4. **Penyusunan Test Suite 62 Kasus Uji:** Menyusun skenario pengujian otomatis untuk memverifikasi setiap kemungkinan akses dari 4 peran pengguna berbeda, integritas endpoint JSON, dan mekanisme toggle star.
- **Keterbatasan AI & Validasi Mandiri oleh Mahasiswa:**
  1. **Penanganan Lingkungan Windows & File System:** Mahasiswa mengidentifikasi adanya anomali penulisan file kosong pada lingkungan sistem operasi lokal dan memastikan setiap file template, migrasi, dan konfigurasi tersimpan dengan benar menggunakan PowerShell UTF-8 encoding.
  2. **Verifikasi Keanggotaan Grup Editor:** Mahasiswa memvalidasi secara langsung bahwa pemeriksaan grup menggunakan case-insensitive `name__iexact="Editor"` agar tangguh terhadap variasi penamaan di Django Admin.
  3. **Verifikasi Manual dan Kontrol Git:** Mahasiswa menguji fungsionalitas aplikasi di peramban, memastikan status HTTP 403 Forbidden muncul tepat saat pengguna yang tidak berhak mencoba mengakses URL edit/tambah/hapus secara langsung, serta mengontrol penuh riwayat commit git.

---

### Tugas 5: Interaktivitas Web dengan JavaScript, AJAX, Popover API, dan Perlindungan XSS

Pada Individual Assignment 5 ini, konsep interaktivitas modern, pemanggilan data asinkronus (AJAX), pengelolaan popover modal, dan perlindungan keamanan terhadap serangan *Cross-Site Scripting* (XSS) yang telah dipelajari pada Tutorial 05 diimplementasikan secara menyeluruh (*end-to-end*) pada entitas portofolio **Experience** (yang berasal dari Tugas 3 dan Tugas 4).

#### 1. Fungsionalitas & Arsitektur yang Diimplementasikan
- **Daftar Pengalaman Asinkronus (AJAX & State Containers):**
  - Halaman `show_experience` (`templates/experience.html`) direfaktor sehingga hanya merender kerangka halaman (*skeleton shell*).
  - Data pengalaman dimuat secara asinkronus dari endpoint `/api/experience/` menggunakan `fetch()`.
  - Terdapat 4 kontainer status visual yang terisolasi dengan baik:
    - `#experience-loading`: Spinner animasi pemuatan data.
    - `#experience-error`: Notifikasi kegagalan jaringan/server beserta tombol *Coba lagi*.
    - `#experience-empty`: Penanganan status data kosong yang dinamis (pesan berbeda saat tidak ada data vs saat pencarian tidak menemukan hasil).
    - `#experience-grid`: Grid kartu pengalaman yang dibangun secara dinamis melalui JavaScript DOM manipulation.
- **Serialisasi Data Manual & Informasi Star Tugas 4:**
  - Endpoint `get_experience_json` (`main/views.py`) menyusun payload JSON secara manual dengan `JsonResponse` dan optimasi query `prefetch_related("starred_by")`.
  - Menyertakan metadata relasi `starred_by`: jumlah total star (`star_count`), status bintang pengguna saat ini (`is_starred`), dan daftar nama pemberi bintang (`starred_by_names`).
- **Pencarian Real-Time dengan Debouncing (300ms):**
  - Mengimplementasikan helper modular `debounce(callback, 300)` pada input pencarian judul/posisi pengalaman.
  - Mengeliminasi request berulang ke server saat pengguna masih mengetik, menyinkronkan query ke URL browser (`history.replaceState`), dan mendukung pembatalan request lama yang belum selesai menggunakan `AbortController`.
- **Penambahan Pengalaman melalui Modal Popover & Fetch API:**
  - Modal form terpadu `templates/components/experience_form_modal.html` menggunakan HTML Popover API (`popover="auto"`), hanya dirender untuk pengguna berstatus `is_superuser`.
  - Pengiriman form ditangani oleh JavaScript melalui Fetch API ke endpoint `create_experience_ajax` dengan metode `POST` dan header `X-CSRFToken` yang diambil dari cookie `csrftoken`.
  - Mengembalikan status HTTP yang semantik: `201 Created` untuk input valid, `400 Bad Request` beserta payload `form.errors.get_json_data()` untuk kesalahan validasi form, dan `403 Forbidden` jika pengguna bukan superuser.
  - Setelah data berhasil disimpan, form di-reset, modal tertutup, feedback instan ditampilkan, dan daftar kartu diperbarui tanpa reload halaman.
- **Sistem Notifikasi Toast Terpadu:**
  - Menggunakan fungsi global `showToast(title, message, type)` (`static/js/toast.js` & `templates/components/toast.html`) untuk memberikan umpan balik visual instan pada aksi penambahan data maupun error validasi.
- **Fitur Interaktif Star melalui AJAX:**
  - Endpoint `toggle_experience_star` mendukung negosiasi konten (`Accept: application/json`). Ketika tombol star ditekan, JavaScript mengirimkan request POST secara asinkronus dan memperbarui elemen tombol serta jumlah bintang secara langsung tanpa reload halaman.
- **Perlindungan Menyeluruh Terhadap Cross-Site Scripting (XSS):**
  - **Sisi Klien (*Client-Side Escaping*):** Seluruh data teks dinamis yang disuntikkan ke dalam template literal HTML dilewatkan melalui fungsi sanitasi `escapeHtml()` (`static/js/utils.js`). Atribut tautan dan gambar divalidasi dengan `safeUrl()` untuk mencegah serangan berbasis URL berbahaya (`javascript:` scheme). Judul pada konfirmasi hapus disisipkan aman melalui `textContent`.
  - **Sisi Server (*Server-Side Sanitization*):** Pada `main/forms.py`, `ExperienceForm` menerapkan metode pembersihan `clean_title`, `clean_category`, dan `clean_description` menggunakan fungsi `strip_tags` dari Django. Jika judul atau deskripsi hanya berisi tag HTML kosong (seperti `<script></script>` atau `<img src="x" onerror="alert(1)">`), form menolaknya dengan `ValidationError`.

---

#### 2. Jawaban Pertanyaan Reflektif

1. **Jelaskan apa itu *debouncing* dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!**
   - **Pengertian *Debouncing*:**
     *Debouncing* adalah teknik optimasi pemrograman yang menunda eksekusi suatu fungsi hingga periode waktu tenang tertentu (*idle delay*) tercapai setelah pemicuan terakhir. Jika event baru terjadi sebelum interval waktu tersebut berakhir, timer penghitungan mundur sebelumnya dibatalkan (`clearTimeout`) dan dihitung ulang dari awal. Fungsi target baru benar-benar dijalankan ketika pengguna berhenti memicu event selama durasi delay yang ditentukan (misalnya 300 milidetik).
   - **Urgensi Penerapannya pada Fitur Pencarian AJAX:**
     - **Mencegah Banjir Permintaan Jaringan (*Preventing Request Flooding*):** Tanpa debouncing, setiap kali pengguna menekan satu tombol keyboard (*event* `input`), browser akan langsung mengirimkan satu HTTP GET request ke server. Sebagai contoh, mengetik kata "Software" (8 karakter) akan memicu 8 request jaringan berturut-turut. Dengan debouncing, hanya 1 request yang dikirim ketika pengguna selesai mengetik kata tersebut.
     - **Mengurangi Beban Komputasi Server dan Basis Data:** Setiap request AJAX pencarian memicu eksekusi query filter SQL (`icontains`), alokasi memori ORM, dan serialisasi JSON di server. Debouncing memangkas beban kerja database dan CPU backend secara drastis.
     - **Menghindari Kondisi Perlombaan (*Race Conditions*):** Permintaan HTTP yang dikirim lebih awal bisa jadi tiba atau selesai diproses lebih lambat daripada permintaan yang dikirim belakangan akibat variasi latensi jaringan. Tanpa debouncing, hasil pencarian usang (*stale response*) dari ketikan awal dapat menimpa hasil pencarian terbaru di layar pengguna.
     - **Efisiensi Bandwidth dan Baterai Klien:** Mengurangi lalu lintas data internet yang tidak perlu dan menghemat daya komputasi perangkat klien, khususnya pengguna perangkat mobile.

2. **Jelaskan fungsi dari penggunaan `await` ketika kita menggunakan `fetch()`! Apa yang akan terjadi jika kita tidak menggunakan `await`?**
   - **Fungsi Penggunaan `await`:**
     - Fungsi `fetch()` secara inheren bersifat asinkronus dan mengembalikan sebuah objek `Promise` yang merepresentasikan operasi jaringan yang sedang berjalan.
     - Kata kunci `await` (yang digunakan di dalam fungsi `async`) berfungsi untuk menghentikan sementara (*pause*) eksekusi fungsi tersebut secara non-blocking hingga `Promise` tersebut diselesaikan (*resolved*) dengan sukses atau ditolak (*rejected*) dengan galat.
     - Melalui `await`, objek `Response` HTTP hasil resolusi diekstrak langsung ke dalam variabel. Pola yang sama berlaku saat memanggil `await response.json()`, di mana `await` menunggu pembacaan aliran data biner (*data stream body*) selesai didekodekan menjadi objek JavaScript murni.
     - Hal ini memungkinkan penulisan kode asinkronus dengan gaya sekuensial yang bersih, linear, mudah dipahami, serta mendukung penanganan galat terpadu menggunakan blok `try ... catch`.
   - **Konsekuensi jika Tidak Menggunakan `await`:**
     - Variabel penerima tidak akan berisi objek data `Response`, melainkan objek `Promise <pending>` yang statusnya belum selesai.
     - Jika kode mencoba membaca properti respons secara langsung (misalnya `const res = fetch(url); if (res.ok) ...`), ekspresi tersebut akan menghasilkan perilaku tidak terduga karena properti `ok` pada Promise bernilai `undefined`.
     - Percobaan memanggil metode pada respons seperti `res.json()` tanpa await akan memicu kegagalan runtime (`TypeError: res.json is not a function`).
     - Alur eksekusi JavaScript akan terus meloncat ke baris kode di bawahnya sebelum data dari server diterima, mengakibatkan manipulasi DOM berjalan dengan data kosong atau memicu crash pada aplikasi.
     - Tanpa `await`, pengembang harus kembali ke pola lama menggunakan *chaining callback* `.then(response => response.json()).then(data => ...).catch(...)` yang rentan terhadap kompleksitas piramida callback (*callback hell*).

3. **Jelaskan apa itu serangan XSS (*Cross-Site Scripting*) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui *template* Django!**
   - **Pengertian Serangan XSS:**
     *Cross-Site Scripting* (XSS) adalah kerentanan keamanan web di mana penyerang berhasil menyuntikkan skrip berbahaya (biasanya JavaScript) ke dalam aplikasi web yang sah. Ketika pengguna lain mengunjungi halaman tersebut, peramban mengeksekusi skrip tersebut dalam konteks sesi dan domain korban. Dampak serangan XSS mencakup pembajakan sesi pengguna (*session hijacking* melalui pencurian cookie), pencurian kredensial, modifikasi tampilan halaman (*defacement*), *keylogging*, hingga eksekusi aksi ilegal tanpa sepengetahuan korban.
   - **Mengapa Data via AJAX/JavaScript Jauh Lebih Rentan Dibanding Template Django:**
     - **Perlindungan Otomatis pada Django Template Engine (*Auto-Escaping*):**
       Template engine bawaan Django secara default menerapkan mekanisme *auto-escaping* pada setiap variabel template `{{ variable }}`. Karakter-karakter khusus HTML yang berpotensi mengeksekusi kode—seperti `<` diubah menjadi `&lt;`, `>` menjadi `&gt;`, `&` menjadi `&amp;`, `"` menjadi `&quot;`, dan `'` menjadi `&#39;`—dinetralkan menjadi teks murni sebelum dikirim ke peramban. Kecuali pengembang secara sengaja menggunakan filter berisiko seperti `|safe` atau tag `{% autoescape off %}`, template Django secara bawaan sangat aman dari XSS.
     - **Penyuntikan Dinamis Berisiko pada JavaScript (`innerHTML`):**
       Pada arsitektur AJAX, peramban menerima data dalam format JSON mentah tanpa pembersihan HTML bawaan. Untuk merender kartu atau elemen antarmuka, pengembang umumnya menyusun *template literals* dan menyuntikkannya ke dalam DOM melalui properti `element.innerHTML`.
       Properti `innerHTML` menginstruksikan mesin peramban untuk mem-parsing dan mengeksekusi seluruh tag HTML yang ada di dalam string tersebut. Jika terdapat data masukan pengguna yang mengandung payload berbahaya—misalnya `<img src="x" onerror="alert('XSS')">` atau `<svg onload="...">`—peramban akan langsung mengeksekusi script tersebut saat elemen disisipkan ke DOM.
     - **Strategi Mitigasi Berlapis (*Defense-in-Depth*):**
       Karena JavaScript tidak memiliki auto-escaping bawaan saat memanipulasi `innerHTML`, aplikasi AJAX wajib menerapkan dua lapis proteksi:
       1. *Client-side Escaping:* Mengubah seluruh karakter sensitif menjadi entitas teks menggunakan fungsi utilitas seperti `escapeHtml()` atau menggunakan properti aman seperti `textContent` dan `document.createTextNode`.
       2. *Server-side Sanitization:* Memvalidasi dan membersihkan tag HTML menggunakan `strip_tags` pada method `clean_<field>` di `ModelForm` sebelum data disimpan ke basis data.

---

### AI Disclosure (Tugas 5)

Pengerjaan Individual Assignment 5 ini memanfaatkan generative AI sebagai asisten pemrograman berpasangan (*pair programming*) dan validasi arsitektur interaktif dengan transparansi sebagai berikut:
- **Tools yang Digunakan:** Gemini (Antigravity Assistant) & Claude.
- **Strategi Prompting:**
  1. **Pendekatan Arsitektur Bersih & Modular (*Shared Utilities First*):** Meminta asisten merancang berkas utilitas bersama `static/js/utils.js` yang menyediakan fungsi reusable (`escapeHtml`, `safeUrl`, `getCookie`, `debounce`, `extractErrorMessages`) sehingga logika frontend tidak diduplikasi di antara `projects.html` dan `experience.html`.
  2. **Konsistensi Desain & Kontinuitas Tugas:** Mempertahankan palet warna, tipografi (*Space Grotesk*), dan estetika Editorial/Neo-Brutalist dari tugas-tugas sebelumnya dengan menyelaraskan kelas styling modal, animasi spinner, kontainer status, serta badge kategori.
  3. **Pengujian Menyeluruh Berbasis TDD (*Test-Driven Development*):** Menyusun test suite otomatis komprehensif pada `main/tests.py` yang menguji seluruh matriks hak akses endpoint AJAX (`create_experience_ajax` dengan kode status 201, 400, 403, 405), endpoint JSON star, serta proteksi sanitasi XSS (total 81 test cases, seluruhnya berstatus `OK`).
- **Aspek Spesifik yang Dibantu:**
  1. **Refaktor Template & AJAX DOM Rendering:** Mengubah `experience.html` menjadi render kerangka murni dan mengonstruksi komponen kartu dinamis dengan JavaScript native, mencakup state loading, error, empty, dan grid.
  2. **Perancangan Endpoint AJAX & Serialisasi JSON:** Mengembangkan fungsi view `create_experience_ajax`, `serialize_experience`, dan memperbarui `get_experience_json` serta `toggle_experience_star` agar merespons JSON secara dinamis.
  3. **Komponen Modal Form Popover:** Membuat `experience_form_modal.html` dan `experience_delete_modal.html` yang terintegrasi dengan HTML Popover API dan CSRF protection.
  4. **Penyusunan 81 Kasus Uji Otomatis:** Mengadaptasi pengujian regresi dan menambahkan kelas uji `Tugas5ExperienceAJAXTest`.
  5. **Analisis Pertanyaan Reflektif:** Berdiskusi secara mendalam mengenai konsep debouncing, mekanisme kerja `async/await`, serta analisis kerentanan XSS pada AJAX vs Django template.
- **Keterbatasan AI & Validasi Mandiri oleh Mahasiswa:**
  1. **Penanganan Isu File System & OneDrive Locking:** Mahasiswa mengidentifikasi bahwa penulisan berkas pada lingkungan Windows dengan sinkronisasi OneDrive aktif dapat memicu rollback berkas jika buffer stream tidak di-flush secara eksplisit. Mahasiswa memastikan setiap berkas disimpan dan dikunci ke disk menggunakan `os.fsync`.
  2. **Pengecekan Karakteristik `strip_tags` Django:** Mahasiswa mendeteksi bahwa payload `<script>alert("XSS")</script>` meninggalkan teks `alert("XSS")` setelah tag dilucuti sehingga tidak kosong. Mahasiswa memvalidasi secara manual dengan payload void tag seperti `<img src="x" onerror="alert(1)">` agar penolakan validasi judul kosong terverifikasi dengan tepat.
  3. **Verifikasi Keamanan Interaktif:** Mahasiswa melakukan verifikasi manual pada browser untuk memastikan bahwa payload XSS tidak tereksekusi dan bahwa hak akses non-superuser tertolak secara konsisten baik di level visual maupun level API backend.
