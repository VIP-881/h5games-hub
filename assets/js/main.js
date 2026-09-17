// H5 Games Hub — 极简交互脚本（无依赖）
(function () {
  'use strict';

  // 页脚年份
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // 游戏卡片标签筛选（可选增强，不影响无 JS 时的可访问性）
  var grid = document.querySelector('.grid');
  if (!grid) return;

  // 渐进增强：为可点击卡片整体添加跳转
  grid.querySelectorAll('article').forEach(function (article) {
    var link = article.querySelector('h3 a');
    if (!link) return;
    article.style.cursor = 'pointer';
    article.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') return; // 链接自身已处理
      window.location.href = link.getAttribute('href');
    });
  });
})();
