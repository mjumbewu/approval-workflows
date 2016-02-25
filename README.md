Approvio
--------

- Each workflow state has a unique random salt
- Approvals/signatures are salted and hashed for verification
- Existing approvals/signatures are verified when reading the request, so that unverified data is never stored.

## Notes

A workflow template is structured something like this:

    {
      "actors": [
        {
          "name": "Applicant"
        },
        {
          "name": "Preparer"
        }
      ]
      "states": [
        {
          "name": "Awaiting Applicant Signature",
          "actor": "Applicant",
          "actions": [
            "sign"
          ],
          "then": [                                          // "then"/"transitions"
            {
              "goto": "Done",                                // "goto"/"next_state"
              "when": "Applicant chooses to sign"            // "when"/"condition"
            },
            {
              "goto": "Awaiting Preparer Signature"
            }
          ]
        },
        {
          "name": "Awaiting Preparer Signature",
          "actor": "Preparer",
          "actions": [
            "sign"
          ],
          "then": [
            {
              "goto": "Done"
            }
          ]
        },
        {
          "name": "Done"
        }
      ],
      "startat": "User 1 Sign"                               // "startat"/"start_state"
    }


- /workflow/:slug/step
  `{ data: ..., state: ... }`

- /workflow/:slug/node/:id/
  CRUD

Examples of actors:
- Applicant
- Employee
- Supervisor
- Travel Committee (a list of people that manage the same queue; any one of them can be a signer)
- CTO

API should, by default, refuse (with a 403) to update a workflow template that is in use, as doing so *may* break any ongoing processes. You can provide a `x-approvio-force` header to force the issue.

----------

Genius notion from @themightychris: Packages could be backed by a Git repository.

Installing Git LFS:

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs
git lfs install
```

Then, for each repo:

```bash
git init
git lfs track "*.psd"
```

----------

If a user wants to use their own GPG key to sign a repository, they'll have to
set up a key first. The instructions for doing so are available from the
[git documentation](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work).

The server will also need its own GPG key to sign commits. You can generate a
GPG key for the server by running:

    gpg --gen-key
