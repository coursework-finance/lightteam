console.log('main.js загружен');

async function api(url, data){
  const r = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  return r.json();
}

async function register(){
  console.log('register() вызвана');

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const full_name = document.getElementById('full_name').value;
  const msg = document.getElementById('msg');

  const r = await api('/cgi-bin/api_register.cgi', {
    email,
    password,
    full_name
  });

  if(r.ok){
    location.href = '/dashboard.html';
  } else {
    msg.innerText = r.error || 'Ошибка регистрации';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded');

  const btn = document.getElementById('regBtn');
  console.log('regBtn =', btn);

  if(btn){
    btn.addEventListener('click', register);
  }
});

async function login(){
  console.log('login() вызвана');

  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const msg = document.getElementById('msg');

  const r = await api('/cgi-bin/api_login.cgi', {
    email,
    password
  });

  if(r.ok){
    location.href = '/dashboard.html';
  } else {
    msg.innerText = r.error || 'Ошибка входа';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const loginBtn = document.getElementById('loginBtn');
  console.log('loginBtn =', loginBtn);

  if(loginBtn){
    loginBtn.addEventListener('click', login);
  }
});

window.register = register;
window.login = login;

document.addEventListener('click', (e) => {
  if (e.target && (e.target.id === 'regBtn' || e.target.id === 'loginBtn')) {
    e.preventDefault();
  }
});

async function loadProfile(){
  try{
    const r = await fetch('/cgi-bin/api_profile.cgi');
    const data = await r.json();

    if(data.ok){
      const el = document.querySelector('.user-name');
      if(el){
        el.innerText = data.full_name || data.email;
      }
    }
  }catch(e){
    console.error('profile load error', e);
  }
}

async function logout(){
  await fetch('/cgi-bin/api_logout.cgi');
  location.href = '/login.html';
}

document.addEventListener('DOMContentLoaded', () => {
  if(document.querySelector('.user-name')){
    loadProfile();
  }
});

async function loadUser(){
  try{
    const r = await fetch('/cgi-bin/api_ping.cgi');
    const data = await r.json();

    if(data.ok){
      const el = document.getElementById('userName');
      if(el){
        el.innerText = data.full_name || data.email || 'Личный кабинет';
      }
    }
  }catch(e){
    console.log('user not logged');
  }
}

async function logout(){
  await fetch('/cgi-bin/api_logout.cgi');
  location.href = '/login.html';
}

document.addEventListener('DOMContentLoaded', loadUser);

document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.user-menu');
  const name = document.querySelector('.user-name');

  if (!menu || !name) return;

  name.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  document.addEventListener('click', () => {
    menu.classList.remove('open');
  });
});

async function addTx(){
  console.log('addTx() вызвана');

  const amount = document.getElementById('amount')?.value;
  const category = document.getElementById('category')?.value;
  const type = document.getElementById('type')?.value;
  const description = document.getElementById('description')?.value;

  if(!amount || !category){
    alert('Введите сумму и категорию');
    return;
  }

  const r = await api('/cgi-bin/api_transactions.cgi', {
    amount,
    category,
    description,
    type
  });

  if(r.ok){
    document.getElementById('amount').value = '';
    document.getElementById('category').value = '';
    document.getElementById('description').value = '';

    loadTransactions();
  } else {
    alert(r.error || 'Ошибка добавления');
  }
}


window.addTx = addTx;

async function loadTransactions(){
  try{
    const r = await fetch('/cgi-bin/api_transactions.cgi');
    const data = await r.json();

    if(!Array.isArray(data)) return;

    const tbody = document.querySelector('#txTable tbody');
    if(!tbody) return;

    tbody.innerHTML = '';

    data.forEach(row => {
      const tr = document.createElement('tr');

      const typeRu = row.type === 'income' ? 'Прибыль' : 'Расход';

      tr.innerHTML = `
        <td>${row.amount}</td>
        <td>${row.category}</td>
        <td>${row.type === 'income' ? 'Прибыль' : 'Расход'}</td>
        <td>${
          new Date(row.created_at.replace(' ', 'T')).toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          })
        }</td>

        <td>${row.description || '—'}</td>
      `;

      tbody.appendChild(tr);
    });

  }catch(e){
    console.error('loadTransactions error', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if(document.getElementById('txTable')){
    loadTransactions();
  }
});

async function loadStats(){
  try{
    const r = await fetch('/cgi-bin/api_stats.cgi');
    const data = await r.json();

    if(data.error) return;

    document.getElementById('statIncome').innerText =
      data.income.toFixed(2) + ' ₽';

    document.getElementById('statExpense').innerText =
      data.expense.toFixed(2) + ' ₽';

    document.getElementById('statBalance').innerText =
      data.balance.toFixed(2) + ' ₽';

    const tip = document.getElementById('financeTip');

    if(data.balance < 0){
      tip.innerText = 'Расходы превышают доходы. Стоит обратить внимание';
    } else if(data.expense > data.income * 0.7){
      tip.innerText = 'Расходы близки к доходам — попробуй начать откладывать часть средств';
    } else {
      tip.innerText = 'Класс! Финансовый баланс в порядке';
    }

  }catch(e){
    console.error('stats error', e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if(document.getElementById('statIncome')){
    loadStats();
  }
});

let chartInstance = null;

async function loadCharts(){
  console.log('loadCharts()');

  const period = document.getElementById('chartPeriod').value;
  const type = document.getElementById('chartType').value;

  let url = '/cgi-bin/api_charts.cgi';

  if(period === 'month'){
    const d = new Date();
    const m = d.toISOString().slice(0,7);
    url += '?month=' + m;
  }

  console.log('fetch:', url);

  const r = await fetch(url);
  const data = await r.json();

  console.log('charts data:', data);

  if(!Array.isArray(data)){
    alert('Ошибка данных аналитики');
    return;
  }

  const tbody = document.querySelector('#chartTable tbody');
  tbody.innerHTML = '';

  const labels = [];
  const values = [];
  const colors = [];

  data.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.category}</td>
      <td>${row.type === 'income' ? 'Прибыль' : 'Расход'}</td>
      <td>${row.total}</td>
    `;
    tbody.appendChild(tr);

    const typeRu = row.type === 'income' ? 'Прибыль' : 'Расход';

    labels.push(`${row.category} (${typeRu})`);
    values.push(row.total);

    colors.push(
      row.type === 'income'
        ? 'rgba(127, 227, 136, 0.7)'
        : 'rgba(101, 225, 239, 0.7)'   
    );
  });

  const canvas = document.getElementById('chartCanvas');
  if(!canvas){
    console.error('canvas not found');
    return;
  }

  const ctx = canvas.getContext('2d');
  if(chartInstance) chartInstance.destroy();

  chartInstance = new Chart(ctx, {
    type: type === 'bar' ? 'bar' : 'pie',
    data: {
      labels,
      datasets: [{
        label: 'Сумма',
        data: values,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.7', '1')),
        borderWidth: 1
      }]
    }
    
  });
}

