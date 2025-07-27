var tabs = function(id) {
  this.el = document.getElementById(id);
  
  this.tab = {
    el: '.tab',
    list: null
  }
  
  this.nav = {
    el: '.tab-nav',
    list: null
  }
  
  this.pag = {
    el: '.tab-pag',
    list: null
  }
  
  this.count = null;
  this.selected = 0;
  
  this.init = function() {
    // Create tabs
    this.tab.list = this.createTabList();
    this.count = this.tab.list.length;
    
    // Create nav
    this.nav.list = this.createNavList();
    this.renderNavList();
    
    // Create pag
    this.pag.list = this.createPagList();
    this.renderPagList();
    
    // Set selected
    this.setSelected(this.selected);
  }
  
  this.createTabList = function() {
    var list = [];
    
    this.el.querySelectorAll(this.tab.el).forEach(function(el, i) {
      list[i] = el;
    });
    
    return list;
  }
  
  this.createNavList = function() {
    var list = [];
    
    this.tab.list.forEach(function(el, i) {
      var listitem = document.createElement('a');
          listitem.className = 'nav-item',
          listitem.innerHTML = el.getAttribute('data-name'),
          listitem.onclick = function() {
            this.setSelected(i);
            return false;
          }.bind(this);
      
      list[i] = listitem;
    }.bind(this));
    
    return list;
  }
  
  this.createPagList = function() {
    var list = [];
    
    list.prev = document.createElement('a');
    list.prev.className = 'pag-item pag-item-prev',
      list.prev.innerHTML = 'Назад',
      list.prev.onclick = function() {
      this.setSelected(this.selected - 1);
      return false;
    }.bind(this);

    list.next = document.createElement('a');
    list.next.className = 'pag-item pag-item-next',
      list.next.innerHTML = 'Вперед',
      list.next.onclick = function() {
      this.setSelected(this.selected + 1);
      return false;
    }.bind(this);
    
    list.submit = document.createElement('button');
    list.submit.className = 'pag-item pag-item-submit',
    list.submit.innerHTML = 'Submit';
    list.submit.name = 'submit';
    
    list.get_json = document.createElement('button');
    list.get_json.className = 'pag-item pag-item-submit';
    list.get_json.innerHTML = 'Скачать JSON';
    list.get_json.name = 'get_json';

    list.add_to_db = document.createElement('button');
    list.add_to_db.className = 'pag-item pag-item-submit';
    list.add_to_db.innerHTML = 'Добавить в БД';
    list.add_to_db.name = 'add_to_db';

    return list;
  }
  
  this.renderNavList = function() {
    var nav = document.querySelector(this.nav.el);
    
    this.nav.list.forEach(function(el) {
      nav.children[0].appendChild(el);
    });
  }
  
  this.renderPagList = function() {
    var pag = document.querySelector(this.pag.el);
    
    pag.children[0].appendChild(this.pag.list.prev);
    pag.children[0].appendChild(this.pag.list.next);
    pag.children[0].appendChild(this.pag.list.submit);
    pag.children[0].appendChild(this.pag.list.get_json);
    pag.children[0].appendChild(this.pag.list.add_to_db);
  }
  
  this.setSelected = function(target) {
    var min = 0,
        max = this.count - 1;
    
    if(target > max || target < min) {
      return;
    }
    
    if(target == min) {
      this.pag.list.prev.classList.add('hidden');
    } else {
      this.pag.list.prev.classList.remove('hidden');
    }
    
    if(target == max) {
      this.pag.list.next.classList.add('hidden');
      this.pag.list.submit.classList.remove('hidden');
      this.pag.list.get_json.classList.remove('hidden');
      this.pag.list.add_to_db.classList.remove('hidden');
    } else {
      this.pag.list.next.classList.remove('hidden');
      this.pag.list.submit.classList.add('hidden');
      this.pag.list.get_json.classList.add('hidden');
      this.pag.list.add_to_db.classList.add('hidden');
    }
    
    this.tab.list[this.selected].classList.remove('selected');
    this.nav.list[this.selected].classList.remove('selected');

    this.selected = target;
    this.tab.list[this.selected].classList.add('selected');
    this.nav.list[this.selected].classList.add('selected');
  }
};

var tabbedForm = new tabs('tabbedForm');
tabbedForm.init();


