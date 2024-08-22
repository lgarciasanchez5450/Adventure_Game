from framework import *
from Colors import * 
from Constants.Display import *
from Utils.Math.Vector import Vector2
from Fonts import *
import Input
from Window import Window
import Window as Window_
from GameUI import HotBarUI, InventoryUI,HealthBar

class GameApp: 
    def __init__(self,window:Window|None = None) -> None:
        window = window or Window((WIDTH,HEIGHT))
        self.window = window
        base_layer.resize(window.size())
        self.inventory_ui = InventoryUI((0,-10),(9,3))
        inventory = Layer(window.size())
        self.game_layer = Layer(self.window.size())

        inventory.space.addObjects(
            BackgroundColor((198,198,198)),
            Aligner(
                self.inventory_ui,
                0.5,1,0.5,1
            )
        )
        self.inventory_layer = Layer(window.size())
        self.inventory_layer.space.addObject(Resizer(inventory,'10%','10%','90%','90%'))
        inventory.space.addObject(KeyBoundFunction(lambda : self.game_layer.removeLayer(self.inventory_layer),'e'))
        inventory.space.addObject(ClearInput())

    def run(self):
        Window_.window = self.window
        import Camera
        import Game_Time
        import general_manager
        import InputGame
        import Settings
        import Textures
        import Time
        Textures._init() 
        healthbar_ui = HealthBar((10 , 10))
        hotbar_ui = HotBarUI()
        game_layer = self.game_layer
        game_layer.space.addObjects(
            Aligner(
                hotbar_ui,
                0.5,1,alignment_y=1
            ),
            Aligner(
                healthbar_ui,
                0.0,0,0,0
            ),
            KeyBoundFunction(lambda : self.game_layer.addLayer(self.inventory_layer),'e')
        )

        Settings.game_state = Settings.GENERATING_WORLD
        for _ in general_manager.generate_world():
            print(_)
        Settings.game_state = Settings.RUNNING
        player = general_manager.Player(Vector2(0,0))
        hotbar_ui.setHotbar(player.hotbar)
        healthbar_ui.setEntity(player)
        self.inventory_ui.setInventory(player.inventory, player.hotbar.spaces)
        general_manager.spawn_entity(player)
        Camera.set_focus(player.pos)
        Camera.set_mouse_pull_strength(13)

        player.hotbar.fitItem(general_manager.Items.SpeedPotion())
        while True:
            Time.update()
            input = Input.getInput()
            if input.quitEvent:
                return 1
            base_layer.update(input)
            game_layer.update(input)
            InputGame.update(input)

            general_manager.step()
            general_manager.update()
            general_manager.update_entities()
            general_manager.manage_chunks()
            Game_Time.update()
            
            Camera.update()
            Camera.draw_background()
            Camera.draw_sprites()
            # Camera.draw_colliders()
            Camera.draw_UI()
            game_layer.draw(self.window.world_surface)
            base_layer.draw(self.window.ui_surface)
            self.window.draw()
            pygame.display.flip()


if __name__ == '__main__':
    GameApp().run()