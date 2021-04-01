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
      for(var i = 0; i < emails.length; i++) {

        // create and style div
        const div = document.createElement('div');
        div.style.border = '1px solid lightgrey';
        div.style.borderRadius = '2px';
        div.style.margin = '10px';
        div.style.padding = '10px';
        // div.id = 'emails'; ?
        if (emails[i].read) {
          div.style.backgroundColor = 'lightgrey';
        }

        // create and append sender
        const sender = document.createElement('span');
        sender.innerHTML = emails[i].sender;
        div.append(sender);

        // create and append timestamp
        const timestamp = document.createElement('span');
        timestamp.innerHTML = emails[i].timestamp;
        timestamp.style.float= 'right';
        div.append(timestamp);

        // break
        const br = document.createElement('br');
        div.append(br);

        // create and append subject
        const subject = document.createElement('strong');
        subject.innerHTML = emails[i].subject ? emails[i].subject : 'No Subject.';
        div.append(subject);
        
        // append div
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
