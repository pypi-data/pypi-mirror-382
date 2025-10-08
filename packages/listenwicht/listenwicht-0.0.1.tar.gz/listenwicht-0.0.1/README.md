# listenwicht
listenwicht is a Python-based, highly flexible client that is able to resend
email according to static redistribution rules. In particular, compared to the
exceptionally simple forwarding configuration, listenwicht actually has an MTA
deliver the mail locally in mboxdir format, where they are picked up and
resent. Before resending, they can be rewritten. This is useful when your MTA
is not a valid according to the set SPF rules. It allows resending from a
SPF-legal "From" address.


## Dependencies
listenwicht depends on the command-line utility `inotifywatch` in order to
monitor the list directory.


## Caveats
listenwicht monitors in the `new/` subdirectory for `CREATE` and `MOVE_TO`
permissions. This is needed because while in newer systems, `MOVE_TO` is called
while on older systems `CREATE` (without any `MODIFY` or `WRITE_CLOSE`) is
used. This means that when testing and writing a file to the `new/`
subdirectory in a non-atomic fashion (e.g., `echo foo >mail.txt`), listenwicht
will misbehave (it might probably try to parse an empty/partial file).


## Usage: MTA setup
First, configure your MTA to perform delivery of emails in a maildir spool
directory. For example, in `main.cf`:

```
mail_spool_directory = /var/spool/mail/
```

Note the trailing slash for the spool directory, which forces maildir mode.

Then, typically, you will want to redirect traffic to a virtual user. For
example, consider there is a `mailinglist` user that listenwicht will run
under. Then, install the Postfix-PCRE module and create a
`/etc/postfix/virtual.pcre` file:

```
/^inf[0-9][0-9]...?[0-9]@my-mailserver\.de$/   mailinglist
/^inf-sgl@my-mailserver\.de$/                  mailinglist
```

This will redirect all traffic to these particular addresses to the maildir
`/var/spool/mail/mailinglist/new`. Enable that PCRE virtual address table by
putting in your `main.cf`:

```
virtual_alias_maps = pcre:/etc/postfix/virtual.pcre
```

Lastly, if you want to filter by `From` addresses, make sure SPF is enabled in
your Postfix configuration for local deliveries.

At this stage, try if you can send mails to postfix and they get accepted. For
example, using the above configuration, write an email to
`inf99abc4@my-mailserver.de` and check the logs to see everything works
properly (SPF configuration, local delivery in the expected directory).


## Usage: listenwicht configuration
When the mails are correctly delivered, you need to setup a listenwicht
configuration file, which is in JSON format. This is an example file, provided
in `example_config.json`:

```json
{
  "rules": [
    {
      "conditions": [
        { "condtype": "match-header", "key": "Message-ID", "regex": "<.*@listenwicht>", "invert": true },
        { "condtype": "match-address", "key": "From", "regex": ".*@allowed-users.de" },
        { "condtype": "match-address", "key": "To", "regex": "inf(23cs1|23cs|23)@.*" }
      ],
      "actions": [
        { "action": "remove-header", "key": [ "Autocrypt", "DKIM-Signature", "Reply-To", "Return-Path", "X-Original-To", "Delivered-To", "Authentication-Results" ] },
        { "action": "rename-header", "old": "From", "new": "Reply-To" },
        { "action": "set-address", "key": "From", "value": [ [ "DHBW Mannheim TINF Mailingliste", "mailinglist@my-mailserver.de" ] ] },
        { "action": "set-address", "key": "To", "value": [ [ "DHBW Mannheim TINF Mailingliste", "mailinglist@my-mailserver.de" ] ] },
        { "action": "set-header", "key": "List-Id", "value": "inf23cs1@my-mailserver.de" },
        { "action": "set-address", "key": "Bcc", "value": [ [ "Cee Ess One", "cs1@foobar.com"], [ "Next cs1 usr", "other@cs1.de" ] ] },
        { "action": "deliver", "via": "smtp://127.0.0.1" }
      ]
    },
    {
      "conditions": [
        { "condtype": "match-header", "key": "Message-ID", "regex": "<.*@listenwicht>", "invert": true },
        { "condtype": "match-address", "key": "From", "regex": ".*@allowed-users.de" },
        { "condtype": "match-address", "key": "To", "regex": "inf(23cs2|23cs|23)@.*" }
      ],
      "actions": [
        { "action": "remove-header", "key": [ "Autocrypt", "DKIM-Signature", "Reply-To", "Return-Path", "X-Original-To", "Delivered-To", "Authentication-Results" ] },
        { "action": "rename-header", "old": "From", "new": "Reply-To" },
        { "action": "set-address", "key": "From", "value": [ [ "DHBW Mannheim TINF Mailingliste", "mailinglist@my-mailserver.de" ] ] },
        { "action": "set-address", "key": "To", "value": [ [ "DHBW Mannheim TINF Mailingliste", "mailinglist@my-mailserver.de" ] ] },
        { "action": "set-header", "key": "List-Id", "value": "inf23cs2@my-mailserver.de" },
        { "action": "set-address", "key": "Bcc", "value": [ [ "CS2 user", "cs2-user@foo.org"], [ "Other CS2 User", "cs2-user-2@invalid.com" ] ] },
        { "action": "deliver", "via": "smtp://127.0.0.1" }
      ]
    },
    {
      "conditions": [
        { "condtype": "match-header", "key": "Message-ID", "regex": "<.*@listenwicht>", "invert": true },
        { "condtype": "match-address", "key": "From", "regex": ".*@allowed-users.de" },
        { "condtype": "match-address", "key": "To", "regex": "inf-sgl@.*" }
      ],
      "actions": [
        { "action": "remove-header", "key": [ "Autocrypt", "DKIM-Signature", "Reply-To", "Return-Path", "X-Original-To", "Delivered-To", "Authentication-Results" ] },
        { "action": "set-address", "key": "From", "value": [ [ "DHBW Mannheim TINF Mailingliste", "inf-sgl@my-mailserver.de" ] ] },
        { "action": "set-address", "key": "To", "value": [ [ "DHBW Mannheim TINF Mailingliste", "mailinglist@my-mailserver.de" ] ] },
        { "action": "set-header", "key": "List-Id", "value": "inf-sgl@my-mailserver.de" },
        { "action": "set-address", "key": "Bcc", "value": [ [ "Admin One", "admin1@foo.org"], [ "Admin Two", "admin2@bar.com" ] ] },
        { "action": "deliver", "via": "smtp://127.0.0.1" }
      ]
    }
  ]
}
```

Note that the first two configuration rules are very similar. The only
difference is that they match different `To` addresses and, therefore,
constitute different lists. When a new email comes in, it is matched against
all rules. If all conditions of a rule apply, the actions are executed.

The first rule checks that the `Message-ID` header is *not* ending in
`@listenwicht>`, which may prevent mail loops. The second condition verifies
that the `From` address is valid (anything from `allowed-users.de` may post to
the list).

The last condition of the first rule verifies that the user of the `To` address
is either `inf23cs1`, `inf23cs`, or `inf23`. Note that the last condition of
the second rule only differes in that it triggers when the `To` address is
either `inf23cs2`, `inf23cs`, or `inf23`. This means that sending to
`inf23cs1@my-mailserver.de` will trigger the first list,
`inf23cs2@my-mailserver.de` will trigger the second list and either
`inf23cs@my-mailserver.de` or `inf23@my-mailserver.de` will trigger *both*.

When a mailing list is triggered, this is what happens:

  - Any header field in the enumeration is completely removed (e.g.,
    `Autocrypt`, `DKIM-Signature`, etc).
  - The `From` header field is rewritten to `Reply-To`. Anything that was
    previously a `From` now is a `Reply-To`.
  - The `From` header field is set to `mailinglist@my-mailserver.de` (which is
    SPF-legal)
  - The `To` header field is set to that same value.
  - A `List-Id` header field is added
  - The recipients of the mail are all added as BCC.
  - The mail is sent via a SMTP connection to `127.0.0.1`.

Note that the example contains a third version which is slightly different in
that the `From` address equates to the mailing list address. This has the
effect that any reply automatically goes to all participants of the mailing
list. In contrast, a reply on the first or seconds list only goes to the
original sender.


## Usage: listenwicht setup
Once you have a configuration file, you can validate the behavior by using the
listenwicht CLI `display` command:

```
$ listenwicht display /var/spool/mail/mailinglist/new/1759833708.V10304I2da2ae1M443121.serenity
Processing mail in 1759822502.V10304I2da679aM490311.serenity
Matching condition: MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>"
Matching condition: MatchAddress field "From" matches regex ".*@allowed-users.de"
Condition result: NOT matched for rule Cond=(MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>") && (MatchAddress field "From" matches regex ".*@allowed-users.de") && (MatchAddress field "To" matches regex "inf(23cs1|23cs|23)@.*") Act=[RemoveHeader, RenameHeader, SetAddress, SetAddress, SetHeader, SetAddress, Deliver]
Matching condition: MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>"
Matching condition: MatchAddress field "From" matches regex ".*@allowed-users.de"
Condition result: NOT matched for rule Cond=(MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>") && (MatchAddress field "From" matches regex ".*@allowed-users.de") && (MatchAddress field "To" matches regex "inf(23cs2|23cs|23)@.*") Act=[RemoveHeader, RenameHeader, SetAddress, SetAddress, SetHeader, SetAddress, Deliver]
Matching condition: MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>"
Matching condition: MatchAddress field "From" matches regex ".*@allowed-users.de"
Condition result: NOT matched for rule Cond=(MatchHeader field "Message-ID" does NOT match regex "<.*@listenwicht>") && (MatchAddress field "From" matches regex ".*@allowed-users.de") && (MatchAddress field "To" matches regex "inf-sgl@.*") Act=[RemoveHeader, SetAddress, SetAddress, SetHeader, SetAddress, Deliver]
```

You can see that the incoming mail triggered none of the three lists, so it
would be silently discarded. You can also see that the failing condition in all
three cases was the `MatchAddress` of the `From` header field. This means the
sender was not permitted to post to the list.

Once you have confidence that your configuration is sound, you can use the
`daemon` facility of listenwicht to continuously watch for incoming mail and
resend them. You can also install a systemd unit for this. First, ensure your
user has lingering enabled (as root):

```
# loginctl enable-linger mailinglist
```

Then, as user `mailinglist`, create a config for example at
`~/.config/listenwicht.json` and install the systemd unit:

```
$ listenwicht systemd --install --config-file ~/.config/listenwicht.json /var/spool/mail/mailinglist
```

That's it!

## License
GNU GPL-3.
