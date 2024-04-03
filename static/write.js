document.addEventListener('DOMContentLoaded', function() {
  var registerForm = document.querySelector('.form_container');
  registerForm.addEventListener('submit', function(event) {
    form_qualification(event);
  });
});
function form_qualification(event) {
  var title = document.getElementById("title").value;
  var content = document.getElementById("content").value;

  var title_qualification = title.length == 0;
  var content_qualification = content.length == 0;
  
  if (title_qualification || content_qualification) {
    if (title_qualification) { alert("제목을 입력해주세요"); }
    if (content_qualification) { alert("내용을 입력해주세요"); }
    event.preventDefault();
  } 
}