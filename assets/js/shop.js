/* ONCOLINK shop: live search by brand and generic name, filters, sort */
(function(){
  var grid = document.getElementById('prod-grid');
  if (!grid) return;
  var qInput = document.getElementById('f-q');
  var catSel = document.getElementById('f-cat');
  var mfrSel = document.getElementById('f-mfr');
  var priceSel = document.getElementById('f-price');
  var stockChk = document.getElementById('f-stock');
  var sortSel = document.getElementById('f-sort');
  var countEl = document.getElementById('shop-count');
  var params = new URLSearchParams(window.location.search);
  var all = [];
  var shown = 0, total = 0;

  function fmt(n){
    return 'Rs ' + Math.round(n).toLocaleString('en-PK');
  }
  function waLink(p){
    var t = 'Hello Oncolink, I need ' + p.name + (p.manufacturer ? ' (' + p.manufacturer + ')' : '') + '. Please share availability and delivery details.';
    return 'https://wa.me/923218406899?text=' + encodeURIComponent(t);
  }
  function priceHtml(p){
    if (p.price_anomaly) return '<div class="prod-price">Call for price</div><div class="prod-note">Price to be confirmed. WhatsApp us.</div>';
    if (!p.has_price) return '<div class="prod-price">Call for price</div><div class="prod-note">WhatsApp us for today\'s price.</div>';
    if (p.price_min === p.price_max) return '<div class="prod-price">' + fmt(p.price_min) + '</div>';
    return '<div class="prod-price">' + fmt(p.price_min) + ' <small>to</small> ' + fmt(p.price_max) + '</div>';
  }
  function card(p){
    var badges = '';
    badges += p.in_stock ? '<span class="badge badge-in">In Stock</span>' : '<span class="badge badge-out">Out of Stock</span>';
    var btn = p.in_stock
      ? '<a class="btn btn-wa btn-block" href="' + waLink(p) + '" target="_blank" rel="noopener">Order on WhatsApp</a>'
      : '<a class="btn btn-outline btn-block" href="' + waLink(p) + '" target="_blank" rel="noopener">Check availability</a>';
    var img = p.image ? '<a href="product/' + p.slug + '.html"><img class="prod-img" src="' + p.image + '" alt="' + esc(p.name) + '" loading="lazy"></a>' : '';
    return '<article class="prod">' + img + badges +
      '<h3><a href="product/' + p.slug + '.html">' + esc(p.name) + '</a></h3>' +
      (p.generic ? '<div class="prod-generic">' + esc(p.generic) + '</div>' : '') +
      (p.manufacturer ? '<div class="prod-mfr">' + esc(p.manufacturer) + '</div>' : '<div class="prod-mfr">&nbsp;</div>') +
      priceHtml(p) + btn + '</article>';
  }
  function esc(s){
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function apply(){
    var q = (qInput.value || '').trim().toLowerCase();
    var cat = catSel.value, mfr = mfrSel.value, pr = priceSel.value;
    var onlyStock = stockChk.checked;
    var list = all.filter(function(p){
      if (cat && p.category !== cat) return false;
      if (mfr && p.manufacturer !== mfr) return false;
      if (onlyStock && !p.in_stock) return false;
      if (pr) {
        var lo = p.price_min || 0, hi = p.price_max || 0;
        if (pr === 'under5k' && lo >= 5000) return false;
        if (pr === '5to25k' && (hi < 5000 || lo > 25000)) return false;
        if (pr === '25to100k' && (hi < 25000 || lo > 100000)) return false;
        if (pr === 'over100k' && hi <= 100000) return false;
        if (pr === 'noprice' && p.has_price) return false;
      }
      if (q) {
        var hay = (p.name + ' ' + p.generic + ' ' + p.manufacturer + ' ' + p.category).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
    var s = sortSel.value;
    if (s === 'low') list.sort(function(a,b){ return (a.price_min||1e12) - (b.price_min||1e12); });
    if (s === 'high') list.sort(function(a,b){ return (b.price_max||0) - (a.price_max||0); });
    if (s === 'az') list.sort(function(a,b){ return a.name.localeCompare(b.name); });
    shown = list.length;
    countEl.textContent = 'Showing ' + shown + ' of ' + total + ' medicines';
    grid.innerHTML = list.length ? list.map(card).join('') :
      '<p style="grid-column:1/-1">No medicine matched your search. Try a different spelling, or WhatsApp us and we will check availability for you.</p>';
  }
  fetch('/data/products.json').then(function(r){ return r.json(); }).then(function(data){
    all = data; total = data.length;
    var cats = {}, mfrs = {};
    data.forEach(function(p){ cats[p.category] = 1; if (p.manufacturer) mfrs[p.manufacturer] = 1; });
    Object.keys(cats).sort().forEach(function(c){
      var o = document.createElement('option'); o.value = c; o.textContent = c + ' (' + data.filter(function(p){return p.category===c;}).length + ')'; catSel.appendChild(o);
    });
    Object.keys(mfrs).sort().forEach(function(m){
      var o = document.createElement('option'); o.value = m; o.textContent = m; mfrSel.appendChild(o);
    });
    var pq = params.get('q'); if (pq) qInput.value = pq;
    var pc = params.get('cat'); if (pc) catSel.value = pc;
    [qInput, catSel, mfrSel, priceSel, stockChk, sortSel].forEach(function(el){
      el.addEventListener('input', apply);
      el.addEventListener('change', apply);
    });
    apply();
  });
})();
