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

function reply_email() {

  self.compose_email();

  // populate form
  document.querySelector('h3').innerText = 'Reply Email';

  const recipients = '';
  const subject = '';
  const body = 'Hello World';

  document.querySelector('#compose-recipients').value = recipients;
  document.querySelector('#compose-subject').value = subject;
  document.querySelector('#compose-body').value = body;
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

      // Show compose view and hide other views
      document.querySelector('#select-email-view').style.display = 'none';
      document.querySelector('#emails-view').style.display = 'block';
      document.querySelector('#compose-view').style.display = 'none';

      load_mailbox('sent')
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

  // save the mailbox name (don't allow archiving from sent mailbox)
  document.querySelector('#emails-view').dataset.mailbox = mailbox;


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
        const header_div = self.email_header_div(email);

        // read emails have grey background
        if (email.read) {
          header_div.classList.add('grey');
        }

        // add email_id to div dataset
        header_div.dataset.email_id = email.id;

        // add div selection function
        header_div.style.cursor = 'pointer';
        header_div.addEventListener('click', function() {

          // pass the email_id to view_email() function
          view_email(this.dataset.email_id);
        });

        // append div
        document.querySelector('#emails-view').append(header_div);
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

  // Show the email and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#select-email-view').style.display = 'block';

  // clear email
  document.querySelector('#select-email-view').innerHTML = '';

  // fetch email
  const path = '/emails/' + id;
  fetch(path)
  .then(response => response.json())
  .then(email => {

      /// add the email html

      // create and append email header div
      const header_div = self.select_email_header_div(email);
      document.querySelector('#select-email-view').append(header_div);

      // create and append email body div
      const body_div = self.email_body_div(email);
      document.querySelector('#select-email-view').append(body_div);

      // archive / unarchive email
      if (document.querySelector('#emails-view').dataset.mailbox != 'sent') {

        // create and append archive/unarchive button
        const button = self.email_archive_button(email.archived, path);
        document.querySelector('#select-email-view').append(button);
      }
      
      // create and append email reply button
      const button = self.email_reply_button();
      document.querySelector('#select-email-view').append(button);


      /// set email as read
      if (!email.read) {

        // set read to true
        fetch(path, {
          method: 'PUT',
          body: JSON.stringify({
              read: true
          })
        })
        // Catch any errors and log them to the console
        .catch(error => {
          console.log('Error:', error);
        });
        // Prevent default submission
        return false;
      }

  })
  // Catch any errors and log them to the console
  .catch(error => {
    console.log('Error:', error);
  });
  // Prevent default submission
  return false;
  
}


function email_reply_button() {

  // reply button
  const button = document.createElement('button');
  button.textContent = 'Reply';
  button.classList.add('reply');
  button.classList.add('btn');
  button.classList.add('btn-primary');

  button.addEventListener('click', function() {
    reply_email();
  });

  return button;
}

function email_archive_button(archived, path) {

  const button = document.createElement('button');
  button.classList.add('btn');
  button.classList.add('btn-outline-primary');
  button.textContent = archived ? 'Unarchive' : 'Archive';

  button.addEventListener('click', async function() {
    const complete = await self.toggle_archive(archived, path);
    self.load_mailbox('inbox')
  });
  
  return button;
}

async function toggle_archive(archived, path) {

  return fetch(path, {
    method: 'PUT',
    body: JSON.stringify({
        archived: !archived
    })
  })
  // Catch any errors and log them to the console
  .catch(error => {
    console.log('Error:', error);
  });

  // Prevent default submission
  return false;
}

function email_body_div(email) {
  
  // create and style div
  const body_div = document.createElement('div');
  body_div.classList.add('section');
  body_div.setAttribute('id', 'email_body');

  // create and append body
  const body = document.createElement('p');
  body.innerHTML = email.body ? email.body : 'No body.';
  body_div.append(body);

  return body_div;
}

function select_email_header_div(email) {

  const header_div = self.email_header_div(email);

  // create and prepend sender prefix
  const from = document.createElement('strong');
  from.innerHTML = 'From: ';
  header_div.prepend(from);

  // create and insert recipients prefix before lastChild
  const to = document.createElement('strong');
  to.innerHTML = 'To: ';
  header_div.insertBefore(to, header_div.lastChild);

  // create and insert recipients before lastChild
  const recipients = document.createElement('span');
  recipients.innerHTML = email.recipients;
  header_div.insertBefore(recipients, header_div.lastChild);

  // insert break before lastChild
  const br = document.createElement('br');
  header_div.insertBefore(br, header_div.lastChild);

  return header_div;
}

function email_header_div(email) {

  // create and style div
  const header_div = document.createElement('div');
  header_div.classList.add('section');

  // create and append sender
  const sender = document.createElement('span');
  sender.setAttribute('id', 'sender');
  sender.innerHTML = email.sender;
  header_div.append(sender);

  // create and append timestamp
  const timestamp = document.createElement('span');
  timestamp.classList.add('timestamp');
  timestamp.innerHTML = email.timestamp;
  header_div.append(timestamp);

  // break
  const br = document.createElement('br');
  header_div.append(br);

  // create and append subject
  const subject = document.createElement('strong');
  subject.setAttribute('id', 'subject');
  subject.innerHTML = email.subject ? email.subject : 'No Subject.';
  header_div.append(subject);
  
  return header_div;
}