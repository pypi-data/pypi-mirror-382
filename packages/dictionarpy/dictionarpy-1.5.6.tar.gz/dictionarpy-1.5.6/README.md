# DictionarPy

An extensible offline dictionary application

The dictionary comes prepopulated with a little over 53,000 words and 118,000
definitions available for offline reference. It is also designed to be
added to and grow with your lexicon.

### Some things you can do:

1. Add and remove words, parts of speech, definitions, IPA transcriptions
2. Show random words
3. Get similar words
4. Reference the built-in IPA key
5. Search within definitions for a particular string

### Statistics regarding this version's included dictionary

```sh
$ dpy -ns
Words:               53300
Definitions:         118827
IPA Transcriptions:  29849
Disk size:           10.52MB
───────────────────────────────────────────────────────
Parts of speech:
    nom féminin │ intransitive verb │ abbreviation
    conjuction │ preposition │ auxiliary verb │ idiom
    nom masculin │ transitive verb │ verb │ article
    transitive/intransitive verb │ phrase │ pronoun
    adverb │ definite article │ abréviation │ plural noun
    │ noun │ adjective │ interjection │ determiner
    conjunction │ nom │ adjectif │ verbe
```

---

## Examples

- Add a word/definition to the database
  
  ```sh
  $ dpy -a -w "my new word" -p "my part of speech" -d "my definition!"
  ```

- Add or update the phonetic/phonemic transcription of a word

  ```sh
  $ dictionarpy -a -w "my new word" -i "/mj nu wɝd/"
  ```

- Show the definitions for a word (use `-n` to avoid ansi escape sequences)

  ```sh
  $ dictionarpy -n "my new word"                                                
  ┌──────────────────────┐
  │     my new word      │
  │     /mj nu wɝd/      │
  ├──────────────────────┤
  │ 1. my part of speech │
  │    my definition!    │
  └──────────────────────┘
  ```

- Remove a definition from the database

  ```sh
  $ dictionarpy -r 1 "my new word"
  ```

- Remove an entry from the database

  ```sh
  $ dictionarpy -R "remove_this_word"
  ```

- Learn a random word!

  ```sh
  $ dpy "$(dpy -z)"
  ```

For help and additional functionality: `dpy -h`
