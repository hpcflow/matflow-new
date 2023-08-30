<img src="https://docs.matflow.io/stable/_static/images/logo-90dpi.png" width="250" alt="MatFlow logo"/>

**Design, run, and share computational materials science workflows**

Documentation: [https://docs.matflow.io/](https://docs.matflow.io/)

## Feature parity with the [old code](https://github.com/LightForm-group/matflow)

This is a list tracking which workflows we have reimplemented/tested in the new code.

| Symbol | Meaning                                                                                |
| ------ | -------------------------------------------------------------------------------------- |
| ✅      | Tested and functional                                                                  |
| ❓      | Untested but should in principle work; may need tweaks to the template parametrisation |
| ❌      | Requires a missing core feature in hpcflow, or a missing software integration          |

| Old workflow                                                                                                        | Status | Docs                                                                              | Notes                                             |
| ------------------------------------------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------------------------- | ------------------------------------------------- |
| [tension_DAMASK_Al](https://github.com/LightForm-group/UoM-CSF-matflow/blob/master/workflows/tension_DAMASK_Al.yml) | ✅      | [Link](https://docs.matflow.io/stable/reference/workflows.html#tension-damask-al) | Available as a demo workflow                      |
| [tension_DAMASK_Mg](https://github.com/LightForm-group/UoM-CSF-matflow/blob/master/workflows/tension_DAMASK_Mg.yml) | ❓      | -                                                                                 | Needs reformatting; and checking hex slip systems |


## Acknowledgements

MatFlow was developed using funding from the [LightForm](https://lightform.org.uk/) EPSRC programme grant ([EP/R001715/1](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/R001715/1))

<img src="https://lightform-group.github.io/wiki/assets/images/site/lightform-logo.png" width="150"/>
