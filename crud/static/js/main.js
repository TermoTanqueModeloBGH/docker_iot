const themeSelector = document.getElementById('theme-selector');
//1. tema guardado al iniciar la pagina
if(themeSelector) {
  const savedTheme = localStorage.getItem('theme') || 'light'; //tema claro por defecto
  //aplicar el tema al atributo de bootstrap en html
  document.documentElement.setAttribute('data-theme', savedTheme);
  //sincroniza el valor del selector visualmente con el tema guardado
  themeSelector.value = savedTheme;
  //2. escuchar cambios en el selector de tema
  themeSelector.addEventListener('change', (e) => {
    const selectedTheme = e.target.value;
    //aplicar el tema seleccionado al atributo de bootstrap en html
    document.documentElement.setAttribute('data-bs-theme', selectedTheme);
    //guardar la preferencia del usuario en localStorage
    localStorage.setItem('theme', selectedTheme);
  });
}
const btnDelete= document.querySelectorAll('.btn-borrar');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  })
}
