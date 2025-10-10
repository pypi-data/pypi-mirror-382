description = "virtual time channel setup"
group = "optional"

excludes = ["counter"]

devices = dict(
    timer = device("nicos.devices.generic.VirtualTimer",
        description = "Virtual timer channel",
        visibility = ()
    ),
)
