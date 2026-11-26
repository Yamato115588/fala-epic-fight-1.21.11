package th.falasiayacraft.phone;

import java.net.URI;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.ConfirmLinkScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

final class PhoneScreen extends Screen {
    private static final URI SITE = URI.create("https://uniz.host/s/fala-siaya-craft");
    private enum Page { HOME, MAP, WEATHER, CALENDAR, BANK, CONFIRM }
    private Page page = Page.HOME;
    private String recipient = "", amount = "";

    PhoneScreen() { super(Component.translatable("item.fala_phone.phone")); }

    @Override protected void init() {
        int x = width / 2 - 68, y = height / 2 - 52;
        if (page == Page.HOME) {
            app(x, y, "gps", () -> navigate(Page.MAP));
            app(x, y + 24, "weather", () -> navigate(Page.WEATHER));
            app(x, y + 48, "calendar", () -> navigate(Page.CALENDAR));
            app(x, y + 72, "web", () -> ConfirmLinkScreen.confirmLinkNow(this, SITE, false));
            if (minecraft.getConnection() != null && minecraft.getConnection().getCommands().getRoot().getChild("pay") != null)
                app(x, y + 96, "bank", () -> navigate(Page.BANK));
        } else if (page == Page.BANK) {
            EditBox player = input(x, y, "recipient", recipient, 16);
            EditBox value = input(x, y + 25, "amount", amount, 14);
            Button review = app(x, y + 49, "review", () -> {
                recipient = player.getValue();
                amount = value.getValue();
                navigate(Page.CONFIRM);
            });
            Runnable validate = () -> review.active = validTransfer(player.getValue(), value.getValue());
            player.setResponder(s -> validate.run());
            value.setResponder(s -> validate.run());
            validate.run();
            app(x, y + 75, "home", () -> navigate(Page.HOME));
        } else if (page == Page.CONFIRM) {
            app(x, y + 60, "send", () -> {
                if (!stillHoldingPhone() || !validTransfer(recipient, amount) || minecraft.getConnection() == null) return;
                minecraft.getConnection().sendCommand("pay " + recipient + " " + amount);
                amount = "";
                recipient = "";
                minecraft.setScreen(null);
            });
            app(x, y + 84, "back", () -> navigate(Page.BANK));
        } else {
            app(x, y + 72, "home", () -> navigate(Page.HOME));
        }
    }

    static boolean validTransfer(String recipient, String amount) {
        return recipient.matches("[A-Za-z0-9_]{3,16}") && amount.matches("(?:[1-9][0-9]{0,8}(?:\\.[0-9]{1,2})?|0\\.(?:[1-9][0-9]?|0[1-9]))");
    }

    private EditBox input(int x, int y, String key, String text, int limit) {
        Component label = Component.translatable("fala_phone." + key);
        EditBox box = addRenderableWidget(new EditBox(font, x, y, 136, 20, label));
        box.setMaxLength(limit);
        box.setHint(label);
        box.setValue(text);
        return box;
    }

    private Button app(int x, int y, String key, Runnable action) {
        return addRenderableWidget(Button.builder(Component.translatable("fala_phone." + key), ignored -> action.run())
            .bounds(x, y, 136, 20).build());
    }

    private void navigate(Page next) { page = next; rebuildWidgets(); }
    @Override public boolean isPauseScreen() { return false; }
    private boolean stillHoldingPhone() {
        return minecraft.player != null && minecraft.player.isHolding(FalaPhone.PHONE);
    }
    @Override public void tick() { if (!stillHoldingPhone()) minecraft.setScreen(null); }
    @Override public void renderBackground(GuiGraphics graphics, int x, int y, float partialTick) {
        // The world stays visible around the phone.
    }

    @Override public void render(GuiGraphics graphics, int mouseX, int mouseY, float partial) {
        int x = width / 2, y = height / 2;
        graphics.fill(x - 78, y - 83, x + 78, y + 74, 0xff202339);
        graphics.drawCenteredString(font, title, x, y - 73, 0xffeee6ff);
        if (minecraft.level != null && minecraft.player != null && page != Page.HOME) {
            var level = minecraft.level;
            var pos = minecraft.player.blockPosition();
            Component data = switch (page) {
                case MAP -> Component.literal("X " + pos.getX() + "   Y " + pos.getY() + "   Z " + pos.getZ());
                case CALENDAR -> Component.translatable("fala_phone.day", Math.floorDiv(level.getDayTime(), 24000L) + 1L);
                case WEATHER -> Component.translatable(level.isThundering() ? "fala_phone.thunder" : level.isRaining() ? "fala_phone.rain" : "fala_phone.clear");
                case CONFIRM -> Component.translatable("fala_phone.confirm", amount, recipient);
                default -> Component.empty();
            };
            graphics.drawCenteredString(font, data, x, y - 10, 0xffffffff);
        }
        super.render(graphics, mouseX, mouseY, partial);
    }

    @Override public void onClose() {
        if (page != Page.HOME) navigate(Page.HOME);
        else super.onClose();
    }
}
