# File Permissions and Service Availability

## Scenario

The `exposure-demo` service runs as a dedicated, non-root user and serves
a static page from `/opt/exposure-demo/index.html`.

The file is owned by `root:root`. With permissions set to `644`, the
service account can read the file but cannot modify it.

## Controlled failure

Removed read permission for others:

```bash
sudo chmod o-r /opt/exposure-demo/index.html
```

The permissions changed from `644` to `640`. The service account was
neither the file owner nor a member of the owning group, so it could no
longer read the page.

A request to `http://127.0.0.1:8080/` returned HTTP 404 even though the
file existed. The service continued responding to requests.

## Investigation

Checked the file's ownership and permissions:

```bash
ls -l /opt/exposure-demo/index.html
```

Reviewed the service logs:

```bash
journalctl -u exposure-demo.service -n 5 --no-pager
```

The logs showed the HTTP 404 but did not identify the permission problem.
The file listing and the service's user configuration provided the
additional context needed to investigate.

## Recovery and verification

Restored read permission for others:

```bash
sudo chmod o+r /opt/exposure-demo/index.html
```

Verified that the page returned HTTP 200:

```bash
curl -i http://127.0.0.1:8080/
```

No service restart was needed.

## Lessons

- A running service can fail to serve content because of file permissions.
- An HTTP 404 does not always mean the requested file is absent.
- Combine application logs with process identity and file permissions.
- The Python server returned 404 for this permission failure; we initially
  expected 403, so we verified the actual behavior instead of assuming it.
