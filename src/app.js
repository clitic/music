/* ================================================
   Trending Music — Application Logic
   ================================================ */

(function () {
    'use strict';

    // ─── SVG Icon Templates ──────────────────────
    const ICONS = {
        views: '<svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>',
        likes: '<svg viewBox="0 0 24 24"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>',
        comments: '<svg viewBox="0 0 24 24"><path d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18z"/></svg>',
        globe: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>'
    };

    // ─── State ────────────────────────────────────
    let data = [];
    let currentIndex = -1;
    let currentDataFile = 'data.json';
    let currentSort = 'views';

    // ─── DOM Refs ─────────────────────────────────
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => document.querySelectorAll(sel);

    const playlistScroll = $('#playlist-scroll');
    const playlistSubtitle = $('#playlist-subtitle');
    const themeBtn = $('#theme-btn');
    const themeIcon = $('#theme-icon');
    const dropdownBackdrop = $('#dropdown-backdrop');
    const lastUpdated = $('#last-updated');

    // ─── Theme Manager ────────────────────────────
    const THEMES = ['adaptive', 'light', 'dark'];
    const THEME_ICONS = {
        adaptive: `<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18V4c4.41 0 8 3.59 8 8s-3.59 8-8 8z"/></svg>`,
        light: `<svg viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 0 0 0-1.41l-1.06-1.06zm1.06-10.96a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg>`,
        dark: `<svg viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/></svg>`
    };

    function getStoredTheme() {
        return localStorage.getItem('yt-music-theme') || 'dark';
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('yt-music-theme', theme);
        if (themeIcon) themeIcon.innerHTML = THEME_ICONS[theme];
        if (themeBtn) themeBtn.setAttribute('aria-label', `Theme: ${theme}`);
    }

    function cycleTheme() {
        const current = getStoredTheme();
        const idx = THEMES.indexOf(current);
        const next = THEMES[(idx + 1) % THEMES.length];
        setTheme(next);
    }

    // ─── Format Helpers ───────────────────────────
    function formatNumber(v) {
        if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
        if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
        if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
        return String(v);
    }

    function timeAgo(isoDate) {
        const diff = Math.max(0, Date.now() - new Date(isoDate).getTime());
        const mins = Math.floor(diff / 60000);
        const hrs = Math.floor(mins / 60);
        const remMins = mins % 60;
        let s = 'Last update ';
        if (hrs > 0) s += `${hrs} hr${hrs > 1 ? 's' : ''} `;
        if (remMins > 0) s += `${remMins} min${remMins > 1 ? 's' : ''} `;
        if (hrs === 0 && remMins === 0) s += 'just now';
        else s += 'ago';
        return s.trim();
    }

    // ─── Data Loading ─────────────────────────────
    function loadData(filename) {
        currentDataFile = filename;
        currentIndex = -1;

        // Show loading state
        if (playlistScroll) {
            playlistScroll.innerHTML = '<div class="empty-state"><div class="loader"></div><span>Loading tracks…</span></div>';
        }

        fetch(filename)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.json();
            })
            .then(d => {
                data = d;
                sortData(currentSort);
            })
            .catch(err => {
                console.error('Load error:', err);
                if (playlistScroll) {
                    playlistScroll.innerHTML = '<div class="empty-state"><span>Failed to load tracks</span></div>';
                }
            });
    }

    function sortData(criteria) {
        currentSort = criteria;
        const sorters = {
            views: (a, b) => b.view_count - a.view_count,
            likes: (a, b) => b.like_count - a.like_count,
            comments: (a, b) => b.comment_count - a.comment_count,
            frequency: (a, b) => b.frequency - a.frequency
        };
        if (sorters[criteria]) data.sort(sorters[criteria]);
        renderPlaylist();
    }

    // ─── Playlist Rendering ───────────────────────
    function renderPlaylist() {
        if (!playlistScroll) return;
        playlistScroll.innerHTML = '';

        data.forEach((song, i) => {
            const item = document.createElement('div');
            item.className = 'pl-item' + (i === currentIndex ? ' active' : '');
            item.setAttribute('data-index', i);
            item.setAttribute('role', 'button');
            item.setAttribute('tabindex', '0');
            item.innerHTML = `
                <div class="pl-item-index">
                    <span class="pl-item-index-text">${i + 1}</span>
                    <div class="pl-item-now">
                        <div class="equalizer">
                            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                        </div>
                    </div>
                </div>
                <img class="pl-item-thumb" src="https://img.youtube.com/vi/${song.id}/mqdefault.jpg" alt="" loading="lazy" />
                <div class="pl-item-info">
                    <div class="pl-item-title">${escapeHtml(song.title)}</div>
                    <div class="pl-item-stats">
                        <span class="pl-stat">${ICONS.views}${formatNumber(song.view_count)}</span>
                        <span class="pl-stat">${ICONS.likes}${formatNumber(song.like_count)}</span>
                        <span class="pl-stat">${ICONS.comments}${formatNumber(song.comment_count)}</span>
                        <span class="pl-stat">${ICONS.globe}${song.frequency.toFixed(1)}%</span>
                    </div>
                </div>
            `;
            item.addEventListener('click', () => selectSong(i));
            item.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectSong(i);
                }
            });
            playlistScroll.appendChild(item);
        });

        if (playlistSubtitle) {
            playlistSubtitle.textContent = `${data.length} tracks`;
        }
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function highlightActive(index) {
        $$('.pl-item').forEach((el, i) => {
            el.classList.toggle('active', i === index);
        });
    }

    // ─── Song Selection ───────────────────────────
    function selectSong(index) {
        if (index < 0 || index >= data.length) return;
        currentIndex = index;
        const song = data[index];
        window.open(`https://youtu.be/${song.id}`, '_blank');
        highlightActive(index);
    }

    // ─── Tab Switching ────────────────────────────
    function initTabs() {
        const tabs = $$('.tab-bar .tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const file = tab.getAttribute('data-file');
                if (file === currentDataFile) return;

                tabs.forEach(t => {
                    t.classList.remove('active');
                    t.setAttribute('aria-selected', 'false');
                });
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');

                loadData(file);
            });
        });
    }

    // ─── Custom Dropdown Logic ────────────────────
    function initDropdowns() {
        const dropdowns = $$('.dropdown');
        dropdowns.forEach(dd => {
            const trigger = dd.querySelector('.dropdown-trigger');
            const menu = dd.querySelector('.dropdown-menu');
            if (!trigger || !menu) return;

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = dd.classList.contains('open');
                closeAllDropdowns();
                if (!isOpen) {
                    dd.classList.add('open');
                    showBackdrop();
                }
            });

            menu.querySelectorAll('.dropdown-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const value = item.getAttribute('data-value');

                    menu.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
                    item.classList.add('selected');

                    const triggerLabel = dd.querySelector('.dropdown-label');
                    if (triggerLabel) {
                        const labels = { views: 'Views', likes: 'Likes', comments: 'Comments', frequency: 'Regions' };
                        triggerLabel.textContent = labels[value] || value;
                    }

                    const action = dd.getAttribute('data-action');
                    if (action === 'sort' && value) {
                        sortData(value);
                    }

                    closeAllDropdowns();
                });
            });
        });

        if (dropdownBackdrop) {
            dropdownBackdrop.addEventListener('click', closeAllDropdowns);
        }

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                closeAllDropdowns();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeAllDropdowns();
        });
    }

    function closeAllDropdowns() {
        $$('.dropdown').forEach(dd => dd.classList.remove('open'));
        hideBackdrop();
    }

    function showBackdrop() {
        if (dropdownBackdrop) dropdownBackdrop.classList.add('visible');
    }

    function hideBackdrop() {
        if (dropdownBackdrop) dropdownBackdrop.classList.remove('visible');
    }

    // ─── Last Update ──────────────────────────────
    async function fetchLastUpdate() {
        try {
            const res = await fetch('https://api.github.com/repos/clitic/music/commits?sha=gh-pages&per_page=1');
            const [commit] = await res.json();
            const isoDate = commit.commit?.committer?.date || commit.commit?.author?.date;
            if (lastUpdated && isoDate) {
                lastUpdated.textContent = timeAgo(isoDate) + '  ·  Updates at IST midnight';
            }
        } catch {
            if (lastUpdated) lastUpdated.textContent = '';
        }
    }

    // ─── Init ─────────────────────────────────────
    function init() {
        setTheme(getStoredTheme());
        initTabs();
        initDropdowns();
        if (themeBtn) themeBtn.addEventListener('click', cycleTheme);
        loadData('data.json');
        fetchLastUpdate();
        setInterval(fetchLastUpdate, 60000);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
