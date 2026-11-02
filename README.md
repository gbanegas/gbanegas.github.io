# cryptme.in — GitHub Pages migration

This is a ready-to-publish static website based on the supplied `index.html`. It uses
**`www.cryptme.in` as the canonical domain**. Links to local PDFs and the profile
image have been converted to paths such as `/files/resume.pdf`, preserving the URLs
visitors use while no longer hard-coding the web host.

## 1. Before changing DNS, collect the assets

The supplied file was **only HTML**. It references 45 separate files (44 PDFs and
one profile image), **not included in this starter ZIP**. On a computer that can
reach your still-running Vultr site, run:

```sh
python3 fetch_assets.py
```

This will put all files at the appropriate paths under `files/` and `images/`.
If any fail (e.g. a file is already missing from the old site), see
`missing_assets.txt` and copy them from Vultr directly into those paths. If the
old site is in `/var/www/html`, you can alternatively copy `files/` and `images/`
from that directory; adapt the actual path to your server. Do **not** change DNS
before completing this step. Avoid committing any unrelated private files.

Note: GitHub Pages does not support Git LFS. If a single asset is >=100 MiB,
host that asset separately instead of adding it to this repository.

## 2. Create the website repository on GitHub

Create a **public** repository named exactly `gbanegas.github.io` under the
GitHub account `gbanegas`. Put these project files in the root of the `main`
branch (do not upload the ZIP as a single file). For example, from this folder:

```sh
git init -b main
git add .
git commit -m 'Migrate cryptme.in to GitHub Pages'
git remote add origin https://github.com/gbanegas/gbanegas.github.io.git
git push -u origin main
```

If you created the GitHub repository with a README or another initial commit,
clone it and copy the website files into that clone instead of initializing an
unrelated history.

## 3. Configure Pages *before* editing public DNS

In the GitHub repository: **Settings > Pages**. Under **Build and deployment**,
choose **Deploy from a branch**, branch `main`, folder `/(root)`, and Save.
Under **Custom domain**, confirm `www.cryptme.in` (the repository also includes
the matching `CNAME` file). GitHub recommends verifying ownership of the domain
using its generated TXT challenge before assigning the custom domain.

## 4. DNS changes at the current authoritative DNS provider

Set:

| Type | Host | Value |
|------|------|-------|
| CNAME | www | gbanegas.github.io |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |

Remove old A/AAAA records for `@` pointing at Vultr and any old `www` A/AAAA
records before setting `www` CNAME. If old `AAAA` records exist for `@`, either
replace them with GitHub's documented IPv6 addresses or remove them. Leave
MX/TXT (email SPF/DKIM/DMARC) and other unrelated records unchanged. Do not
change your domain registration or nameservers just for web hosting.

After DNS propagation, in GitHub Pages check DNS, confirm the TLS certificate,
and enable **Enforce HTTPS**. Then test both `https://www.cryptme.in` and
`https://cryptme.in`, as well as `/images/profile.png`, `/files/resume.pdf`,
and a few `/files/papers/...` links, before stopping Vultr.

## Verification commands

```sh
dig +short CNAME www.cryptme.in
dig +short A cryptme.in
curl -I https://www.cryptme.in/
curl -I https://www.cryptme.in/files/resume.pdf
```

See https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
