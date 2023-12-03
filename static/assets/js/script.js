function submitForm(id) {
  var form = document.getElementById(id);
  var formData = new FormData(form);
  var durationInput = form.elements['duration'];
  if (durationInput) {
    var durationValue = durationInput.value;

    // Überprüfe, ob die eingegebene Dauer maximal 04:00 ist
    var maxTime = new Date(0, 0, 0, 4, 0, 0); // 04:00 Uhr
    var enteredDuration = new Date(0, 0, 0, durationValue.split(':')[0], durationValue.split(':')[1], 0);

    if (enteredDuration > maxTime) {
      alert('You are over the maximum time');
      return;
    }
  }

  fetch('/api', {
    method: 'POST',
    body: formData
  })
  .then(response => {
    window.location.href = "https://wmtd.frieda-univers.me/";
  })
  .catch(error => {
    console.error('error', error);
  });
}

function reloadPage() {
  window.location.href = "https://wmtd.frieda-univers.me/";
}
setTimeout(reloadPage, 30000);
