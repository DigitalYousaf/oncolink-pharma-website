/* ONCOLINK main JS: mobile nav, FAQ accordion, WhatsApp forms */
(function(){
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function(){ nav.classList.toggle('open'); });
  }
  document.querySelectorAll('.faq-q').forEach(function(btn){
    btn.addEventListener('click', function(){
      btn.parentElement.classList.toggle('open');
    });
  });
  var heroS = document.getElementById('hero-search');
  if (heroS) {
    heroS.addEventListener('submit', function(e){
      e.preventDefault();
      var q = document.getElementById('hero-search-input').value.trim();
      window.location.href = '/shop.html' + (q ? '?q=' + encodeURIComponent(q) : '');
    });
  }
  // Contact form -> WhatsApp
  var cf = document.getElementById('contact-form');
  if (cf) {
    cf.addEventListener('submit', function(e){
      e.preventDefault();
      var name = document.getElementById('cf-name').value.trim();
      var phone = document.getElementById('cf-phone').value.trim();
      var topic = document.getElementById('cf-topic').value;
      var msg = document.getElementById('cf-msg').value.trim();
      var text = 'Hello Oncolink, my name is ' + name + '. Phone: ' + phone + '. Topic: ' + topic + '. Message: ' + msg;
      window.open('https://wa.me/923218406899?text=' + encodeURIComponent(text), '_blank');
    });
  }
  // B2B quote form -> WhatsApp
  var qf = document.getElementById('quote-form');
  if (qf) {
    qf.addEventListener('submit', function(e){
      e.preventDefault();
      var org = document.getElementById('qf-org').value.trim();
      var name = document.getElementById('qf-name').value.trim();
      var phone = document.getElementById('qf-phone').value.trim();
      var type = document.getElementById('qf-type').value || 'Not specified';
      var msg = document.getElementById('qf-msg').value.trim();
      var text = 'Hello Oncolink, hospital/pharmacy quote request. Organisation: ' + org + '. Contact person: ' + name + '. Phone: ' + phone + '. Type: ' + type + '. Details: ' + msg;
      window.open('https://wa.me/923218406899?text=' + encodeURIComponent(text), '_blank');
    });
  }
  // Price check form -> WhatsApp
  var pf = document.getElementById('price-form');
  if (pf) {
    pf.addEventListener('submit', function(e){
      e.preventDefault();
      var med = document.getElementById('pf-med').value.trim();
      var text = 'Hello Oncolink, please share the price and availability of: ' + med;
      window.open('https://wa.me/923218406899?text=' + encodeURIComponent(text), '_blank');
    });
  }
})();
