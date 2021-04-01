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
  document.querySelector('#select-email-view').style.display = 'none';
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
  document.querySelector('#select-email-view').style.display = 'none';

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

        email = emails[i];
        const div = self.display_email(email);

        // add email_id to div dataset
        div.dataset.email_id = email.id;

        // add div selection function
        div.style.cursor = 'pointer';
        div.onclick = function () {
          // pass the email_id to view_email() 
          view_email(this.dataset.email_id);
        };

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

function view_email(id) {
  console.log('VIEW_EMAIL ID:');
  console.log(id);

  // Show the email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#select-email-view').style.display = 'block';

  // Show the mailbox name
  // document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  const path = '/emails/' + id;
  fetch(path)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);

      // add the email html

      // email header
      const div = self.display_email(email);

      // create and prepend sender prefix
      const from = document.createElement('span');
      from.innerHTML = 'From: ';
      div.prepend(from); // no div!

      // create and insert recipients before lastChild
      const to = document.createElement('span');
      to.innerHTML = 'To: ' + email.recipients;
      div.insertBefore(to, div.lastChild);

      // insert break before lastChild
      const br = document.createElement('br');
      div.insertBefore(br, div.lastChild);

      // append header div
      document.querySelector('#select-email-view').append(div);


      // email body
      // create and style div
      const body_div = document.createElement('div');
      body_div.style.border = '1px solid lightgrey';
      body_div.style.borderRadius = '2px';
      body_div.style.margin = '10px';
      body_div.style.padding = '10px';

      // create and append body
      const body = document.createElement('p');
      body.innerHTML = email.body ? email.body : 'No body.';
      body_div.append(body);

      // append body div
      document.querySelector('#select-email-view').append(body_div);
  })
  // Catch any errors and log them to the console
  .catch(error => {
    console.log('Error:', error);
  });
  // Prevent default submission
  return false;;
}

function display_email(email) {
  // create and style div
  const div = document.createElement('div');
  div.style.border = '1px solid lightgrey';
  div.style.borderRadius = '2px';
  div.style.margin = '10px';
  div.style.padding = '10px';
  if (email.read) {
    // read emails have grey background
    div.style.backgroundColor = 'lightgrey';
  }

  // create and append sender
  const sender = document.createElement('span');
  sender.innerHTML = email.sender;
  div.append(sender);

  // create and append timestamp
  const timestamp = document.createElement('span');
  timestamp.innerHTML = email.timestamp;
  timestamp.style.float= 'right';
  div.append(timestamp);

  // break
  const br = document.createElement('br');
  div.append(br);

  // create and append subject
  const subject = document.createElement('strong');
  subject.innerHTML = email.subject ? email.subject : 'No Subject.';
  div.append(subject);
  
  return div;
}