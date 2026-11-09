/**
 * Helper JavaScript bersama untuk halaman-halaman AJAX (Projects, Experience, dst.).
 * Dimuat di base.html sehingga setiap halaman cukup memanggil fungsinya.
 */

/**
 * Mengubah karakter khusus HTML menjadi entity agar nilai ditampilkan sebagai teks biasa.
 * Wajib dipakai untuk SETIAP nilai dinamis yang disisipkan lewat innerHTML (pencegahan XSS).
 */
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

/**
 * Hanya meloloskan URL yang aman (http, https, atau relative path).
 * Mencegah URL berbahaya seperti `javascript:alert(1)` dipakai pada atribut href/src.
 */
function safeUrl(value) {
    try {
        const str = String(value ?? '').trim();
        if (!str) return '';
        if (str.startsWith('/') || str.startsWith('http://') || str.startsWith('https://')) {
            return str;
        }
        return '';
    } catch (error) {
        return '';
    }
}

/** Membaca nilai cookie, digunakan untuk mengambil token CSRF (`csrftoken`). */
function getCookie(name) {
    if (!document.cookie) return null;
    const prefix = name + '=';
    const match = document.cookie
        .split(';')
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(prefix));
    return match ? decodeURIComponent(match.substring(prefix.length)) : null;
}

/**
 * Membungkus fungsi agar baru dijalankan setelah tidak dipanggil selama `delay` ms.
 */
function debounce(callback, delay = 300) {
    let timerId;
    const debounced = (...args) => {
        clearTimeout(timerId);
        timerId = setTimeout(() => callback(...args), delay);
    };
    debounced.cancel = () => clearTimeout(timerId);
    return debounced;
}

/**
 * Mengubah respons error JSON dari server menjadi daftar pesan yang mudah dibaca.
 * Mendukung format DRF (`{"title": ["..."]}`, `{"detail": "..."}`) maupun
 * format lama (`{"errors": form.errors.get_json_data()}`, `{"message": "..."}`).
 */
function extractErrorMessages(result, status) {
    if (result && typeof result === 'object') {
        if (result.errors) {
            return Object.values(result.errors).flat().map(error => error.message || String(error));
        }
        if (typeof result.detail === 'string') {
            return [result.detail];
        }
        if (typeof result.message === 'string') {
            return [result.message];
        }
        const flatMessages = Object.values(result)
            .flat()
            .filter(val => typeof val === 'string');
        if (flatMessages.length > 0) {
            return flatMessages;
        }
    }
    return [`Terjadi kesalahan (HTTP ${status}).`];
}
