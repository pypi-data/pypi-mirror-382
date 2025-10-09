from textual.app import App, ComposeResult
from textual.widgets import Input, Label
from textual.containers import Vertical
from ipaddress import IPv4Interface, AddressValueError, NetmaskValueError

class SubnetCalcApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
    Input {
        width: 40;
    }
    """

    # Reactive variable to store the current character count

    def clear(self):
        self.ip_address.update("")
        self.subnet_with_netmask.update("")
        self.subnet_with_prefix.update("")
        self.network.update("")
        self.broadcast.update("")
        self.total_addresses.update("")
        self.error.update("")


    def compose(self) -> ComposeResult:
        # Create the input and counter label
        self.input = Input(placeholder="10.0.0.1/24")
        self.ip_address = Label("")
        self.error = Label("")
        self.subnet_with_netmask = Label("")
        self.subnet_with_prefix = Label("")
        self.network = Label("")
        self.broadcast = Label("")
        self.total_addresses= Label("")
        yield Vertical(
                self.input,
                self.error,
                self.ip_address,
                self.subnet_with_netmask,
                self.subnet_with_prefix,
                self.network,
                self.broadcast,
                self.total_addresses,
                )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Called whenever the text in the input changes."""
        self.clear()
        if len(event.value) > 0:
            try:
                self.ip_network = IPv4Interface(event.value)
                self.ip_address.update(f"IP Address: {self.ip_network.ip}")
                self.subnet_with_netmask.update(f"Netmask: {self.ip_network.with_netmask.split('/')[1]}")
                self.subnet_with_prefix.update(f"Prefix: /{self.ip_network.with_prefixlen.split('/')[1]}")
                self.network.update(f"Network: {self.ip_network.network.network_address}")
                self.broadcast.update(f"Broadcast: {self.ip_network.network.broadcast_address}")
                self.total_addresses.update(f"Total addresses: {self.ip_network.network.num_addresses}")

                self.error.update("")
            except AddressValueError as e:
                self.error.update(str(e))
            except NetmaskValueError as e:
                self.error.update(str(e))


def main():
    SubnetCalcApp().run()


if __name__ == "__main__":
    main()

