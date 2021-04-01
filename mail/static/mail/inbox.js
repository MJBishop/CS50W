document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  /// 
  document.querySelector('form').onsubmit = send_email;
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function send_email() {

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
  })
  // Catch any errors and log them to the console
  .catch(error => {
    console.log('Error:', error);
  });
  // Prevent default submission
  return false;
  
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  //
  const path = '/emails/' + mailbox;
  fetch(path)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);

      // add emails ...
      // emails.forEach(obj => {
      for(var i = 0; i < emails.length; i++) {

        const div = document.createElement('div');

        const header = document.createElement('h3');
        header.innerHTML = emails[i].sender;
        div.append(header);

        const label = document.createElement('label');
        label.innerHTML = emails[i].subject;
        div.append(label);
        
        const span = document.createElement('span');
        span.innerHTML = emails[i].timestamp;
        div.append(span);

        document.querySelector('#emails-view').append(div);
      };
  })
  // Catch any errors and log them to the console
  .catch(error => {
    console.log('Error:', error);
  });
  // Prevent default submission
  return false;;
}
