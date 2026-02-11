import { useState } from 'react'
import { Box, Flex, Input, Container, Heading, Text, Button } from '@chakra-ui/react'
import { Settings, Smartphone } from 'lucide-react'
import Dashboard from './components/Dashboard'

function App() {
    const [ipAddress, setIpAddress] = useState('localhost')
    const [inputIp, setInputIp] = useState('localhost')
    const [isConfigOpen, setIsConfigOpen] = useState(false)

    const handleSaveConfig = () => {
        setIpAddress(inputIp)
        setIsConfigOpen(false)
    }

    return (
        <Box minH="100vh" bg="#f7fafc" color="gray.800" fontFamily="'Inter', sans-serif">
            <Container maxW="container.xl" py={8}>
                {/* Header */}
                <Flex justify="space-between" align="center" mb={10} py={4} borderBottom="1px solid" borderColor="gray.200">
                    <Flex align="center" gap={3}>
                        <Box p={2} bg="teal.50" borderRadius="lg" color="teal.500">
                            <Smartphone size={28} />
                        </Box>
                        <Heading size="lg" letterSpacing="tight" color="gray.700">
                            ServerSure <Text as="span" color="gray.400" fontSize="md" fontWeight="medium">Monitor</Text>
                        </Heading>
                    </Flex>

                    <Flex gap={4}>
                        <Button
                            variant="ghost"
                            color="gray.600"
                            _hover={{ bg: 'gray.100', color: 'teal.600' }}
                            onClick={() => setIsConfigOpen(!isConfigOpen)}
                        >
                            <Settings size={18} />
                            <Text ml={2} display={{ base: 'none', md: 'block' }}>Config</Text>
                        </Button>
                    </Flex>
                </Flex>

                {/* Config Panel */}
                {isConfigOpen && (
                    <Box
                        mb={10}
                        p={6}
                        bg="white"
                        borderRadius="xl"
                        border="1px solid"
                        borderColor="gray.200"
                        boxShadow="sm"
                    >
                        <Heading size="sm" mb={4} color="gray.600" textTransform="uppercase" letterSpacing="wide" fontSize="xs">Configuration</Heading>
                        <Flex gap={4} align="flex-end">
                            <Box flex={1}>
                                <Text mb={2} fontSize="sm" color="gray.500">Raspberry Pi IP Address</Text>
                                <Input
                                    value={inputIp}
                                    onChange={(e) => setInputIp(e.target.value)}
                                    placeholder="e.g., 192.168.1.50"
                                    bg="gray.50"
                                    borderColor="gray.200"
                                    _focus={{ borderColor: 'teal.400', boxShadow: 'none' }}
                                    color="gray.800"
                                />
                            </Box>
                            <Button colorScheme="teal" bg="teal.500" color="white" _hover={{ bg: 'teal.600' }} onClick={handleSaveConfig}>
                                Save & Connect
                            </Button>
                        </Flex>
                    </Box>
                )}

                {/* Dashboard Content - passing down styles implicitly via context or just prop drilling logic */}
                <Dashboard ipAddress={ipAddress} />

            </Container>
        </Box>
    )
}

export default App
