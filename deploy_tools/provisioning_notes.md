Provisioning the website
=========================
## Required packages:
* nginx
* Python3
* virtualenv + pip
* git

## Configuring Nginx:

* see nginx.template.conf
* replace SITENAME with the actual site name

## Systemd service

* see gunicorn-systemd.template.service
* replace SITENAME with the actual site name

## Folder structure:
If user home directory in /home/username

/home/username
└── sites
    └── SITENAME
        ├── database
        ├── source
        ├── static
        └── virtualenv 