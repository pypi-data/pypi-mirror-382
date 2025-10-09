#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from typing import cast

logger = logging.getLogger(__name__)


class Requires:
    """Create a tuple with package dependencies."""

    __slots__ = (
        'data', 'name', 'options', 'option_for_resolve_off'
    )

    def __init__(self, data: dict[str, dict[str, str]], name: str, options: dict[str, bool]) -> None:
        self.data = data
        self.name = name
        logger.debug("Initializing Requires for package '%s'.", self.name)

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)
        logger.debug("Option 'option_resolve_off' is set to %s.", self.option_for_resolve_off)

    def resolve(self) -> tuple[str, ...]:
        """Resolve the dependencies.

        Return package dependencies in the right order.
        """
        logger.info("Resolving dependencies for package '%s'.", self.name)
        dependencies: tuple[str, ...] = ()

        if not self.option_for_resolve_off:
            if self.name not in self.data:
                logger.error("Package '%s' not found in data. Cannot resolve dependencies.", self.name)
                return dependencies

            requires: list[str] = self.remove_deps(cast(list[str], self.data[self.name]['requires']))
            logger.debug("Initial direct dependencies for '%s': %s", self.name, requires)

            for require in requires:
                if require not in self.data:
                    logger.warning("Dependency '%s' for package '%s' not found in data. Skipping.", require, self.name)
                    continue

                sub_requires: list[str] = self.remove_deps(cast(list[str], self.data[require]['requires']))
                logger.debug("Found sub-dependencies for '%s': %s", require, sub_requires)

                for sub in sub_requires:
                    if sub in self.data and sub not in requires:
                        requires.append(sub)
                        logger.debug("Added transitive dependency '%s' to the list.", sub)
                    else:
                        logger.debug("Skipping sub-dependency '%s' (already exists or not in data).", sub)

            requires.reverse()
            dependencies = tuple(dict.fromkeys(requires))
            logger.info("Final resolved dependencies for '%s': %s", self.name, dependencies)

        return dependencies

    def remove_deps(self, requires: list[str]) -> list[str]:
        """Remove requirements that not in the repository.

        Args:
            requires (list[str]): List of requires.

        Returns:
            list: List of packages name.
        """
        initial_count = len(requires)
        filtered_requires = [req for req in requires if req in self.data]
        removed_count = initial_count - len(filtered_requires)

        if removed_count > 0:
            removed_deps = [req for req in requires if req not in self.data]
            logger.debug("Removed %d dependencies that are not in the repository: %s", removed_count, removed_deps)

        logger.debug("Filtered dependencies list size: %d", len(filtered_requires))
        return filtered_requires
