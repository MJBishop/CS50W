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
        const header_div = self.email_header_div(email);

        if (email.read) {
          // read emails have grey background
          header_div.style.backgroundColor = 'lightgrey';
        }

        // add email_id to div dataset
        header_div.dataset.email_id = email.id;

        // add div selection function
        header_div.style.cursor = 'pointer';
        header_div.onclick = function () {
          // pass the email_id to view_email() 
          view_email(this.dataset.email_id);
        };

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


  const path = '/emails/' + id;

  // fetch email
  fetch(path)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);

      // add the email html

      /// email header
      const header_div = self.email_header_div(email);

      // create and prepend sender prefix
      const from = document.createElement('span');
      from.innerHTML = 'From: ';
      header_div.prepend(from);

      // create and insert recipients before lastChild
      const to = document.createElement('span');
      to.innerHTML = 'To: ' + email.recipients;
      header_div.insertBefore(to, header_div.lastChild);

      // insert break before lastChild
      const br = document.createElement('br');
      header_div.insertBefore(br, header_div.lastChild);

      // append header div
      document.querySelector('#select-email-view').append(header_div);


      /// email body
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

function email_header_div(email) {

  // create and style div
  const header_div = document.createElement('div');
  header_div.style.border = '1px solid lightgrey';
  header_div.style.borderRadius = '2px';
  header_div.style.margin = '10px';
  header_div.style.padding = '10px';

  // create and append sender
  const sender = document.createElement('span');
  sender.innerHTML = email.sender;
  header_div.append(sender);

  // create and append timestamp
  const timestamp = document.createElement('span');
  timestamp.innerHTML = email.timestamp;
  timestamp.style.float= 'right';
  header_div.append(timestamp);

  // break
  const br = document.createElement('br');
  header_div.append(br);

  // create and append subject
  const subject = document.createElement('strong');
  subject.innerHTML = email.subject ? email.subject : 'No Subject.';
  header_div.append(subject);
  
  return header_div;
}