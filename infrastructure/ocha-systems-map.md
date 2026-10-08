---
content_type: infrastructure
last_reviewed: "2026-10-08"
# The URL is declared once, with the KB's other published products, in automation.md's surfaces list.
---

# OCHA systems map

A map of the data systems around the team: the ones OCHA runs for response planning and
monitoring, pooled funds and information services, the services of the wider UN Secretariat
they stand on, and the outside sources we read. It shows which unit owns each system, where
it is hosted, what kind of thing it is, and how data moves between them and into our mirror
schemas. A Costs tab gives an estimated running cost for each system and says how firm each
figure is: stated, priced from an inventory, or guessed outright. Cost figures taken from
internal documents are left out of this copy; they are on the private one.

**<https://ocha-dap.github.io/ds-knowledge-base/systems-map/>** — behind a passphrase; ask
the data science team.

## Why it is behind a passphrase, and where the source is

The map draws on internal material: the organisational charts, a read-only look at OCHA's
Azure subscription, and registers on OCHA's intranet. So its source is not in this repository.
It lives in the private `ds-knowledge-base-internal` repository (the write-up is
`infrastructure/ocha-data-systems-landscape.md` there; the generator is
`scripts/gen_systems_map.py`), where people who can read that repository also get an
unencrypted copy on its private Pages site.

What is committed here is only `encrypted/systems-map.html`: the page encrypted with
[staticrypt](https://github.com/robinmoisson/staticrypt), which the site workflow copies to
`/systems-map/` after checking that it is encrypted. It is refreshed by running
`scripts/publish_systems_map.sh` in the internal repository, which takes the passphrase from
the environment and has no default. Do not edit the encrypted file by hand, and never commit a
readable copy.

One shared passphrase is a low wall: anyone who has it can pass it on, and the encrypted file
can be downloaded and attacked offline. Treat what the map holds as internal to the team
rather than as public, and keep credentials, addresses and network detail out of it.

## Related

- [Database ER map](db-erd.md): every table of our own databases, open, no passphrase. The
  systems map's table level sets the same tables beside the upstream systems they mirror.
- [Database network map](https://ocha-dap.github.io/ds-knowledge-base/db-network/): which
  jobs and apps read and write our databases.
