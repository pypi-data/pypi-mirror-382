use bevy::prelude::*;
use bevy::window::PrimaryWindow;
use crate::app::AppState;
use crate::drone::TargetEvent;
use crate::geometry::{RootVolume, Volume};
use super::{PrimaryMenu, Scroll, UiText, UiWindow, WindowLocation};


pub fn build(app: &mut App) {
    app
        .add_event::<UpdateEvent>()
        .add_systems(OnEnter(AppState::Display), setup_window.after(PrimaryMenu::spawn))
        .add_systems(Update, (
            on_button,
            on_update.after(on_button)

        ).run_if(in_state(AppState::Display)));
}

#[derive(Component)]
struct VolumeContent;

pub fn setup_window(
    mut commands: Commands,
    root: Query<Entity, With<RootVolume>>,
    primary_menu: Query<Entity, With<PrimaryMenu>>,
    primary_window: Query<&Window, With<PrimaryWindow>>,
    children: Query<&Children, With<Volume>>,
    volumes: Query<&Volume>,
) -> Result<()> {
    let Ok(primary_window) = primary_window.single() else { return Ok(()) };

    let content = commands.spawn((
        VolumeContent,
        Node {
            display: Display::Flex,
            flex_direction: FlexDirection::Column,
            ..default()
        },
    )).id();

    let mut scroll = Scroll::spawn(&mut commands, &primary_window);
    scroll.add_child(content);
    let scroll = scroll.id();

    let mut window = UiWindow::new("Volumes", WindowLocation::Relative, &mut commands);
    window.add_child(scroll);
    let window = window.id();

    commands
        .entity(primary_menu.single()?)
        .add_child(window);

    update_window(
        content,
        &mut commands,
        &root,
        &children,
        &volumes,
    )
}

#[derive(Event)]
struct UpdateEvent(Entity, bool);

fn on_button(
    interactions: Query<(&Interaction, &VolumeButton, &Children), Changed<Interaction>>,
    keyboard_input: Res<ButtonInput<KeyCode>>,
    mut text_query: Query<&mut TextColor>,
    volumes: Query<&Volume>,
    mut ev_target: EventWriter<TargetEvent>,
    mut ev_update: EventWriter<UpdateEvent>,
) {
    for (interaction, button, children) in interactions.iter() {
        let mut text_color = text_query.get_mut(children[0]).unwrap();
        match *interaction {
            Interaction::Pressed => {
                if keyboard_input.pressed(KeyCode::ShiftLeft) {
                    let volume = volumes.get(button.0).unwrap();
                    ev_target.write(TargetEvent(volume.target()));
                } else {
                    let recursive = keyboard_input.pressed(KeyCode::ControlLeft);
                    ev_update.write(UpdateEvent(button.0, recursive));
                }
                text_color.0 = UiText::PRESSED.into();
            }
            Interaction::Hovered => {
                text_color.0 = UiText::HOVERED.into();
            }
            Interaction::None => {
                text_color.0 = UiText::NORMAL.into();
            }
        }
    }
}

fn on_update(
    mut commands: Commands,
    mut events: EventReader<UpdateEvent>,
    menu: Query<Entity, With<VolumeContent>>,
    root: Query<Entity, With<RootVolume>>,
    children: Query<&Children, With<Volume>>,
    mut volumes: Query<&mut Volume>,
) -> Result<()> {
    for event in events.read() {
        let mut volume = volumes.get_mut(event.0)?;
        volume.expanded = !volume.expanded;
        if event.1 {
            fn recurse(
                expanded: bool,
                entity: Entity,
                children: &Query<&Children, With<Volume>>,
                volumes: &mut Query<&mut Volume>,
            ) -> Result<()> {
                let Ok(childs) = children.get(entity) else { return Ok(()) };
                for child in childs {
                    let mut volume = volumes.get_mut(*child)?;
                    volume.expanded = expanded;
                    recurse(expanded, *child, children, volumes)?;
                }
                Ok(())
            }
            recurse(volume.expanded, event.0, &children, &mut volumes)?;
        }
        update_window(
            menu.single()?,
            &mut commands,
            &root,
            &children,
            &volumes.as_readonly(),
        )?;
    }
    Ok(())
}

fn update_window(
    content: Entity,
    commands: &mut Commands,
    root: &Query<Entity, With<RootVolume>>,
    children: &Query<&Children, With<Volume>>,
    volumes: &Query<&Volume>,
) -> Result<()> {
    fn add_button(
        depth: usize,
        entity: Entity,
        content: Entity,
        commands: &mut Commands,
        children: &Query<&Children, With<Volume>>,
        volumes: &Query<&Volume>,
    ) -> Result<()> {
        let volume = volumes.get(entity)?;
        let childs = children.get(entity).ok();
        let qualifier = if childs.is_some() && !volume.expanded {
            ".."
        } else {
            ""
        };
        let label = format!("{}{}{}", "  ".repeat(depth), volume.name, qualifier);
        let button = VolumeButton::spawn_button(label.as_str(), entity, commands);
        commands
            .entity(content)
            .add_child(button);
        if volume.expanded {
            if let Some(childs) = childs {
                for child in childs {
                    add_button(depth + 1, *child, content, commands, children, volumes)?;
                }
            }
        }
        Ok(())
    }

    clear_window(content, commands);
    add_button(0, root.single()?, content, commands, children, volumes)
}

fn clear_window(content: Entity, commands: &mut Commands) {
    let mut content = commands.entity(content);
    content.despawn_related::<Children>();
}

#[derive(Component)]
pub struct VolumeButton(Entity);

impl VolumeButton {
    fn spawn_button(
        message: &str,
        volume: Entity,
        commands: &mut Commands,
    ) -> Entity {
        let component = VolumeButton(volume);
        UiText::spawn_button(component, message, commands)
    }
}
