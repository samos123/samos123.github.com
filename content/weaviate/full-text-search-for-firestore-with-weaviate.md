Title: Full Text Search for Firestore with Weaviate
Date: 2022-11-03 11:36
Author: Sam Stoelinga
Category: Weaviate
Tags: weaviate, firestore, firebase, search
Slug: full-text-search-for-firestore-with-weaviate

Many applications require searching through large text fields
in your firestore database. For example, you might need to search
through articles containing a specific word.

Cloud Firestore does not have support for indexing of text fields. So 3rd
party solutions such as Weaviate or ElasticSearch are required for Full-Text
Search.

This blog post describes how to integrate Weaviate with Firestore to enable
Full Text search for an example Note taking application. At a high-level 
the following will be done:

1. Deploy Weaviate and define the Schema in Weaviate
2. Create a Firebase Function to index Notes automatically when a note is created
3. Create a Firebase Function to Search the indexed Notes using Weaviate


### Deploy Weaviate and define Schema
You can use Weaviate Cloud Service or you can deploy Weaviate yourself by
choosing one of the [self-deploy options here](https://weaviate.io/developers/weaviate/current/getting-started/installation.html#running-weaviate-yourself).

This blog post uses the Weaviate Cloud Service because that provides us
with an easy to use public endpoint for Weaviate. Ensure Enable OIDC Authenication
is set to "Disabled". Note that this endpoint is accessible by anyone
on the internet and doesn't require authentication. So this
isn't suitable for production and for demo purposes only


Install Weaviate Javascript client:
```bash
mkdir firestore-weaviate-test
cd firestore-weaviate-test
npm install weaviate-client
```


Let's define the Weaviate Schema for our Note taking application. Currently this
is stored in Firestore in the following way:
```
// /notes/${ID}
{
  owner: "{UID}", // Firebase Authentication's User ID of note owner
  text: "This is my first note!"
}
```

Now let's define our Schema to index the Firestore Note. Create a file named
`schema-creation.js` with the following content:
```
const weaviate = require("weaviate-client");

const client = weaviate.client({
    scheme: "http",
    // IMPORTANT replace your-wcs-instance with your actual WCS instance
    host: "your-wcs-instance.semi.network",
});

var classObj = {
  "class": "Note",
  "description": "An index for Full-Search of notes in Firestore",
  "properties": [
      {
          "dataType": [
              "string"
          ],
          "description": "The ID of the note",
          "name": "nid",
      },
      {
          "dataType": [
              "string"
          ],
          "description": "The Firebase Authentication UID of the creator of the note",
          "name": "uid"
      },
      {
          "dataType": [
              "text"
          ],
          "description": "The content of the note",
          "name": "text"
      }
  ]
}

client
  .schema
  .classCreator()
  .withClass(classObj)
  .do()
  .then(res => {
    console.log(res)
  })
  .catch(err => {
    console.error(err)
  });
```
Review the file and make sure you changed `your-wcs-instance` to your actual
instance name. Alternatively, change the connection section to connect to
your self deployed Weaviate instance.

Execute the Schema creation script by running:
```bash
node schema-creation.js
```

Weaviate is now ready to start indexing notes. You can import existing
notes by following the documention on [importing data into Weaviate](https://weaviate.io/developers/weaviate/current/getting-started/import.html).

### Indexing Firestore Notes automatically on creation
A Firebase Function can be used to automatically insert a Note into the
Weaviate index when it is created. This assumes you've already created
a Firebase project, if not, please create a firebase project first.

Initialize Firebase in your current working directly:
```
firebase init firestore
firebase init functions # say no to eslint
```
The above command will create a directory named functions inside your
current working directory.

Change to the functions directory and install weaviate-client:
```bash
cd functions
npm install weaviate-client
```

Open the file `index.js` and replace it with the following content:
```
const functions = require("firebase-functions");
const weaviate = require("weaviate-client");
const WEAVIATE_HOST = functions.config().weaviate.host;
const OPENAI_APIKEY = functions.config().weaviate.openaiapikey;

const client = weaviate.client({
    scheme: "https", // http or https
    host: WEAVIATE_HOST,
    headers: { "X-OpenAI-Api-Key": OPENAI_APIKEY },
});

// Update the search index every time a note is created.
exports.onNoteCreated = functions.firestore
    .document("notes/{noteId}")
    .onCreate(async (snap, context) => {
        // Get the note document
        const note = snap.data();

        // Use the 'nodeId' path segment as the identifier for Elastic
        const id = context.params.noteId;
        client.data
            .creator()
            .withClassName("Note")
            .withProperties({
                nid: id,
                uid: note.uid,
                text: note.text,
            })
            .do()
            .then((res) => {
                console.log(res);
            })
            .catch((err) => {
                console.error(err);
            });
    });
```

Configure the Firebase Environment based on your own values. Run the following
command but replace the values to match your environment:
```bash
firebase functions:config:set weaviate.host="your-wcs-instance.semi.network" weaviate.openaiapikey="yourverysecretAPIkey"
```

Deploy the function by running:
```bash
firebase deploy --only functions
```

Let's try creating many notes (7k+) in Firestore to test the function. Create a file
named `create-notes.js` with the following content:
```javascript
const {
    initializeApp,
    applicationDefault,
    cert,
} = require("firebase-admin/app");
const {
    getFirestore,
    Timestamp,
    FieldValue,
} = require("firebase-admin/firestore");
const fs = require("fs");
const { parse } = require("csv-parse");

initializeApp({
    credential: applicationDefault(),
});

const db = getFirestore();

var parser = parse({ columns: true }, function (err, records) {
    records.forEach(async (record) => {
        const docRef = await db.collection("notes").add({
            uid: "same",
            text: record.description,
        });
    });
});

fs.createReadStream(__dirname + "/wine_reviews.csv").pipe(parser);
```

Download a demo dataset that contains wine reviews. We'll use the content
for the notes.
```bash
curl -O https://raw.githubusercontent.com/semi-technologies/weaviate-examples/main/semanticsearch-transformers-wines/data/wine_reviews.csv
```

The code for creating notes requires application default credentials. Let's
configure your Google Application Default credentials by running the following:
```bash
gcloud config set project your-firebase-project-name
gcloud auth application-default login
```

Install the node-csv dependency by running:
```bash
npm install csv-parse
```

Create the notes in Firestore by running:
```bash
node create-notes.js
```

Verify the notes have also been created in Weaviate by running this GraphQL
query in Weaviate:
```
{
  Get {
    Note {
      text
    }
  }
}
```

### Creating a Firebase Function to search using Weaviate
Let's add another firebase function by adding the following code at the bottom of `index.js`:
```javascript
exports.searchNotes = functions.https.onCall(async (data, context) => {
    const concepts = data.concepts;

    const notes = await client.graphql
        .get()
        .withClassName("Note")
        .withFields("nid uid text")
        .withNearText({
            concepts: concepts,
            distance: 0.6,
        })
        .do();
    console.log(notes)

    return {notes: notes.data.Get.Note};
});
```

Deploy the updated functions to Firebase by running:
```bash
firebase deploy --only functions
```

Afterwards, you can use the firebase callable function in your Firebase
app like this:
```javascript
var searchNotes = firebase.functions().httpsCallable('searchNotes');
searchNotes({concepts: ["light fruity wine"]}).then( (result) => {
    const notes = result.data.notes;
    console.log(notes[0]); // print the 1st result
});
```

### Conclusion
This blog post demonstrated how to implement Full Text Semantic Search for
Firestore by using Weaviate. The index in Weaviate is automatically updated
whenever a new document is added to Firestore. OpenAI is used to automatically
generate a vector for the text field. The firebase callable function makes it
easy to search through the database using Weaviate without having to call
Weaviate directly.

### Security note
The setup in this blog post uses an unauthenticated Weaviate setup. Depending on your
requirements, you might need to configure some form of authentication between
the Cloud Function and your Weaviate instance.
