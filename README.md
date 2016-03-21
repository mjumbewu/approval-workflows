Workflow Approvals
------------------

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
              "when": "'{{action}}' == 'sign'"               // "when"/"condition"
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



Examples of actors:
- Applicant
- Employee
- Supervisor
- Travel Committee (a list of people that manage the same queue; any one of them can be a signer)
- CTO


----------

Genius notion from @themightychris: Package could be backed by a Git repository.
Data could be committed to repo, and signature/approval/action could be a tag.
Commits and tags would be signed with GPG key to prevent tampering. For uber-
secutiry, certain workflows could require tags to be signed with personal GPG
key for extra verifiability.

Documents have to be checked in to repo too.

----------

If a user wants to use their own GPG key to sign a repository, they'll have to
set up a key first. The instructions for doing so are available from the
[git documentation](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work).

The server will also need its own GPG key to sign commits. You can generate a
GPG key for the server by running:

    gpg --gen-key
