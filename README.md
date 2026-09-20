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